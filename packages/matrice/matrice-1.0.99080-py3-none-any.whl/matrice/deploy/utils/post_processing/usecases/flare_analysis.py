"""
Flare Analysis Use Case for Post-Processing

This module provides flare analysis functionality with color detection,
height analysis, and alert generation.
"""

from typing import Any, Dict, List, Optional
from dataclasses import asdict, dataclass, field
import time
from datetime import datetime, timezone
import tempfile
import os
import cv2
import numpy as np
from collections import defaultdict

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol
from ..core.config import BaseConfig, AlertConfig
from ..utils import (
    filter_by_confidence,
    filter_by_categories,
    apply_category_mapping,
    match_results_structure,
    extract_major_colors,
    bbox_smoothing,
    BBoxSmoothingConfig,
    BBoxSmoothingTracker
)


@dataclass
class FlareAnalysisConfig(BaseConfig):
    """Configuration for flare analysis use case."""
    # Smoothing configuration
    enable_smoothing: bool = True
    smoothing_algorithm: str = "observability"
    smoothing_window_size: int = 20
    smoothing_cooldown_frames: int = 5
    smoothing_confidence_range_factor: float = 0.5

    # Confidence thresholds
    confidence_threshold: float = 0.5

    # Color analysis
    top_k_colors: int = 3

    # Frame processing
    frame_skip: int = 1
    fps: Optional[float] = None

    # Categories
    usecase_categories: List[str] = field(default_factory=lambda: ["BadFlare", "GoodFlare"])
    target_categories: List[str] = field(default_factory=lambda: ["BadFlare", "GoodFlare"])

    # Category mapping
    index_to_category: Optional[Dict[int, str]] = field(
        default_factory=lambda: {0: "BadFlare", 1: "GoodFlare"}
    )

    # Alert configuration
    alert_config: Optional[AlertConfig] = None

    # Tracking
    time_window_minutes: int = 60
    enable_unique_counting: bool = True

    def validate(self) -> List[str]:
        errors = super().validate()
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            errors.append("confidence_threshold must be between 0 and 1")
        if self.top_k_colors <= 0:
            errors.append("top_k_colors must be positive")
        if self.frame_skip <= 0:
            errors.append("frame_skip must be positive")
        if self.smoothing_window_size <= 0:
            errors.append("smoothing_window_size must be positive")
        if self.smoothing_cooldown_frames < 0:
            errors.append("smoothing_cooldown_frames cannot be negative")
        if self.smoothing_confidence_range_factor <= 0:
            errors.append("smoothing_confidence_range_factor must be positive")
        return errors


class FlareAnalysisUseCase(BaseProcessor):
    # Human-friendly display names for categories
    CATEGORY_DISPLAY = {
        "BadFlare": "Bad Flare",
        "GoodFlare": "Good Flare"
    }

    def __init__(self):
        super().__init__("flare_analysis")
        self.category = "flare_detection"
        self.CASE_TYPE: Optional[str] = "flare_detection"
        self.CASE_VERSION: Optional[str] = "1.2"

        # List of categories to track
        self.target_categories = ["BadFlare", "GoodFlare"]

        # Initialize trackers
        self.smoothing_tracker = None
        self.tracker = None

        # Tracking state variables
        self._total_frame_counter = 0
        self._global_frame_offset = 0
        self._tracking_start_time = None
        self._track_aliases: Dict[Any, Any] = {}
        self._canonical_tracks: Dict[Any, Dict[str, Any]] = {}
        self._track_merge_iou_threshold: float = 0.05
        self._track_merge_time_window: float = 7.0
        self._ascending_alert_list: List[int] = []
        self.current_incident_end_timestamp: str = "N/A"
        self._per_category_total_track_ids = {cat: set() for cat in self.target_categories}
        self._current_frame_track_ids = {cat: set() for cat in self.target_categories}

    def process(
        self,
        data: Any,
        config: ConfigProtocol,
        context: Optional[ProcessingContext] = None,
        input_bytes: Optional[bytes] = None,
        stream_info: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        start_time = time.time()
        if not isinstance(config, FlareAnalysisConfig):
            return self.create_error_result(
                "Invalid config type", usecase=self.name, category=self.category, context=context
            )
        if context is None:
            context = ProcessingContext()
        if not input_bytes:
            return self.create_error_result(
                "input_bytes required for flare analysis", usecase=self.name, category=self.category, context=context
            )
        if not data:
            return self.create_error_result(
                "Detection data required", usecase=self.name, category=self.category, context=context
            )

        # Detect input format
        input_format = match_results_structure(data)
        context.input_format = input_format
        context.confidence_threshold = config.confidence_threshold
        self.logger.info(f"Processing flare analysis with format: {input_format.value}")

        # Filter and map data
        processed_data = filter_by_confidence(data, config.confidence_threshold)
        if config.index_to_category:
            processed_data = apply_category_mapping(processed_data, config.index_to_category)
        processed_data = [d for d in processed_data if d.get("category") in self.target_categories]

        # Apply bbox smoothing
        if config.enable_smoothing:
            if self.smoothing_tracker is None:
                smoothing_config = BBoxSmoothingConfig(
                    smoothing_algorithm=config.smoothing_algorithm,
                    window_size=config.smoothing_window_size,
                    cooldown_frames=config.smoothing_cooldown_frames,
                    confidence_threshold=config.confidence_threshold,
                    confidence_range_factor=config.smoothing_confidence_range_factor,
                    enable_smoothing=True
                )
                self.smoothing_tracker = BBoxSmoothingTracker(smoothing_config)
            processed_data = bbox_smoothing(processed_data, self.smoothing_tracker.config, self.smoothing_tracker)

        # Advanced tracking
        try:
            from ..advanced_tracker import AdvancedTracker
            from ..advanced_tracker.config import TrackerConfig
            if self.tracker is None:
                tracker_config = TrackerConfig()
                self.tracker = AdvancedTracker(tracker_config)
                self.logger.info("Initialized AdvancedTracker for flare analysis")
            processed_data = self.tracker.update(processed_data)
        except Exception as e:
            self.logger.warning(f"AdvancedTracker failed: {e}")

        # Update tracking state
        self._update_tracking_state(processed_data)
        self._total_frame_counter += 1

        # Extract frame number
        frame_number = None
        if stream_info:
            input_settings = stream_info.get("input_settings", {})
            start_frame = input_settings.get("start_frame")
            end_frame = input_settings.get("end_frame")
            if start_frame is not None and end_frame is not None and start_frame == end_frame:
                frame_number = start_frame

        # Analyze flares
        flare_analysis = self._analyze_flares_in_media(processed_data, input_bytes, config)
        counting_summary = self._count_categories(flare_analysis, config)
        counting_summary["total_counts"] = self.get_total_counts()
        alerts = self._check_alerts(counting_summary, frame_number, config)
        predictions = self._extract_predictions(flare_analysis)

        # Generate outputs
        incidents_list = self._generate_incidents(counting_summary, alerts, config, frame_number, stream_info)
        tracking_stats_list = self._generate_tracking_stats(counting_summary, alerts, config, frame_number, stream_info)
        business_analytics_list = self._generate_business_analytics(counting_summary, alerts, config, frame_number, stream_info, is_empty=True)
        summary_list = self._generate_summary(counting_summary, incidents_list, tracking_stats_list, business_analytics_list, alerts)

        # Extract frame-based dictionaries
        incidents = incidents_list[0] if incidents_list else {}
        tracking_stats = tracking_stats_list[0] if tracking_stats_list else {}
        business_analytics = business_analytics_list[0] if business_analytics_list else {}
        summary = summary_list[0] if summary_list else {}
        agg_summary = {
            str(frame_number) if frame_number is not None else "current_frame": {
                "incidents": incidents,
                "tracking_stats": tracking_stats,
                "business_analytics": business_analytics,
                "alerts": alerts,
                "human_text": summary
            }
        }

        context.mark_completed()
        result = self.create_result(
            data={"agg_summary": agg_summary},
            usecase=self.name,
            category=self.category,
            context=context
        )
        if config.confidence_threshold < 0.3:
            result.add_warning(f"Low confidence threshold ({config.confidence_threshold}) may result in false positives")
        processing_time = context.processing_time or time.time() - start_time
        self.logger.info(f"Flare analysis completed in {processing_time:.2f}s")
        return result

    def _is_video_bytes(self, media_bytes: bytes) -> bool:
        video_signatures = [
            b'\x00\x00\x00\x20ftypmp4', b'\x00\x00\x00\x18ftypmp4', b'RIFF', b'\x1aE\xdf\xa3', b'ftyp'
        ]
        for signature in video_signatures:
            if media_bytes.startswith(signature) or signature in media_bytes[:50]:
                return True
        return False

    def _analyze_flares_in_media(self, data: Any, media_bytes: bytes, config: FlareAnalysisConfig) -> List[Dict[str, Any]]:
        is_video = self._is_video_bytes(media_bytes)
        return self._analyze_flares_in_video(data, media_bytes, config) if is_video else self._analyze_flares_in_image(data, media_bytes, config)

    def _analyze_flares_in_video(self, data: Any, video_bytes: bytes, config: FlareAnalysisConfig) -> List[Dict[str, Any]]:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            temp_video.write(video_bytes)
            video_path = temp_video.name
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError("Failed to open video file")
            fps = config.fps or cap.get(cv2.CAP_PROP_FPS)
            flare_analysis = []
            frame_id = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_id % config.frame_skip != 0:
                    frame_id += 1
                    continue
                frame_key = str(frame_id)
                timestamp = frame_id / fps
                frame_detections = self._get_frame_detections(data, frame_key)
                if not frame_detections:
                    frame_id += 1
                    continue
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                for detection in frame_detections:
                    if detection.get("confidence", 1.0) < config.confidence_threshold:
                        continue
                    bbox = detection.get("bounding_box", detection.get("bbox"))
                    if not bbox:
                        continue
                    crop = self._crop_bbox(rgb_frame, bbox, config.bbox_format)
                    if crop.size == 0:
                        continue
                    major_colors = extract_major_colors(crop, k=config.top_k_colors)
                    main_color = major_colors[0][0] if major_colors else "unknown"
                    flare_record = {
                        "frame_id": frame_key,
                        "timestamp": round(timestamp, 2),
                        "category": detection.get("category", "unknown"),
                        "confidence": round(detection.get("confidence", 0.0), 3),
                        "main_color": main_color,
                        "major_colors": major_colors,
                        "bbox": bbox,
                        "detection_id": detection.get("id", f"det_{len(flare_analysis)}"),
                        "track_id": detection.get("track_id")
                    }
                    flare_analysis.append(flare_record)
                frame_id += 1
            cap.release()
            return flare_analysis
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)

    def _analyze_flares_in_image(self, data: Any, image_bytes: bytes, config: FlareAnalysisConfig) -> List[Dict[str, Any]]:
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError("Failed to decode image from bytes")
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        flare_analysis = []
        detections = self._get_frame_detections(data, "0")
        for detection in detections:
            if detection.get("confidence", 1.0) < config.confidence_threshold:
                continue
            bbox = detection.get("bounding_box", detection.get("bbox"))
            if not bbox:
                continue
            crop = self._crop_bbox(rgb_image, bbox, config.bbox_format)
            if crop.size == 0:
                continue
            major_colors = extract_major_colors(crop, k=config.top_k_colors)
            main_color = major_colors[0][0] if major_colors else "unknown"
            flare_record = {
                "frame_id": "0",
                "timestamp": 0.0,
                "category": detection.get("category", "unknown"),
                "confidence": round(detection.get("confidence", 0.0), 3),
                "main_color": main_color,
                "major_colors": major_colors,
                "bbox": bbox,
                "detection_id": detection.get("id", f"det_{len(flare_analysis)}"),
                "track_id": detection.get("track_id")
            }
            flare_analysis.append(flare_record)
        return flare_analysis

    def _get_frame_detections(self, data: Any, frame_key: str) -> List[Dict[str, Any]]:
        if isinstance(data, dict):
            return data.get(frame_key, [])
        elif isinstance(data, list):
            return data
        return []

    def _crop_bbox(self, image: np.ndarray, bbox: Dict[str, Any], bbox_format: str) -> np.ndarray:
        h, w = image.shape[:2]
        if bbox_format == "auto":
            bbox_format = "xmin_ymin_xmax_ymax" if "xmin" in bbox else "x_y_width_height"
        
        if bbox_format == "xmin_ymin_xmax_ymax":
            xmin = max(0, int(bbox["xmin"]))
            ymin = max(0, int(bbox["ymin"]))
            xmax = min(w, int(bbox["xmax"]))
            ymax = min(h, int(bbox["ymax"]))
            x_center = (xmin + xmax) / 2
            x_offset = (xmax - xmin) / 4
            y_center = (ymin + ymax) / 2
            y_offset = (ymax - ymin) / 4
            new_xmin = max(0, int(x_center - x_offset))
            new_xmax = min(w, int(x_center + x_offset))
            new_ymin = max(0, int(y_center - y_offset))
            new_ymax = min(h, int(y_center + y_offset))
        elif bbox_format == "x_y_width_height":
            x = max(0, int(bbox["x"]))
            y = max(0, int(bbox["y"]))
            width = int(bbox["width"])
            height = int(bbox["height"])
            xmax = min(w, x + width)
            ymax = min(h, y + height)
            x_center = (x + xmax) / 2
            x_offset = (xmax - x) / 4
            y_center = (y + ymax) / 2
            y_offset = (ymax - y) / 4
            new_xmin = max(0, int(x_center - x_offset))
            new_xmax = min(w, int(x_center + x_offset))
            new_ymin = max(0, int(y_center - y_offset))
            new_ymax = min(h, int(y_center + y_offset))
        else:
            return np.zeros((0, 0, 3), dtype=np.uint8)
        
        return image[new_ymin:new_ymax, new_xmin:new_xmax]

    def _count_categories(self, detections: List[Dict], config: FlareAnalysisConfig) -> Dict:
        counts = {}
        category_colors = defaultdict(lambda: defaultdict(int))
        for det in detections:
            cat = det.get("category", "unknown")
            counts[cat] = counts.get(cat, 0) + 1
            main_color = det.get("main_color", "unknown")
            category_colors[cat][main_color] += 1
        return {
            "total_count": sum(counts.values()),
            "per_category_count": counts,
            "color_distribution": dict(category_colors),
            "detections": [
                {
                    "bounding_box": det.get("bbox"),
                    "category": det.get("category"),
                    "confidence": det.get("confidence"),
                    "track_id": det.get("track_id"),
                    "frame_id": det.get("frame_id"),
                    "main_color": det.get("main_color"),
                    "major_colors": det.get("major_colors")
                }
                for det in detections
            ]
        }

    def _check_alerts(self, summary: Dict, frame_number: Any, config: FlareAnalysisConfig) -> List[Dict]:
        def get_trend(data, lookback=900, threshold=0.6):
            window = data[-lookback:] if len(data) >= lookback else data
            if len(window) < 2:
                return True
            increasing = 0
            total = 0
            for i in range(1, len(window)):
                if window[i] >= window[i - 1]:
                    increasing += 1
                total += 1
            ratio = increasing / total
            return ratio >= threshold

        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        alerts = []
        total_detections = summary.get("total_count", 0)
        total_counts_dict = summary.get("total_counts", {})
        per_category_count = summary.get("per_category_count", {})

        if not config.alert_config:
            return alerts

        if hasattr(config.alert_config, "count_thresholds") and config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total_detections > threshold:
                    alerts.append({
                        "alert_type": getattr(config.alert_config, "alert_type", ["Default"]),
                        "alert_id": f"alert_{category}_{frame_key}",
                        "incident_category": self.CASE_TYPE,
                        "threshold_level": threshold,
                        "ascending": get_trend(self._ascending_alert_list, lookback=900, threshold=0.8),
                        "settings": {t: v for t, v in zip(
                            getattr(config.alert_config, "alert_type", ["Default"]),
                            getattr(config.alert_config, "alert_value", ["JSON"])
                        )}
                    })
                elif category in per_category_count:
                    count = per_category_count[category]
                    if count > threshold:
                        alerts.append({
                            "alert_type": getattr(config.alert_config, "alert_type", ["Default"]),
                            "alert_id": f"alert_{category}_{frame_key}",
                            "incident_category": self.CASE_TYPE,
                            "threshold_level": threshold,
                            "ascending": get_trend(self._ascending_alert_list, lookback=900, threshold=0.8),
                            "settings": {t: v for t, v in zip(
                                getattr(config.alert_config, "alert_type", ["Default"]),
                                getattr(config.alert_config, "alert_value", ["JSON"])
                            )}
                        })
        return alerts

    def _generate_incidents(
        self, counting_summary: Dict, alerts: List, config: FlareAnalysisConfig,
        frame_number: Optional[int] = None, stream_info: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        incidents = []
        total_detections = counting_summary.get("total_count", 0)
        current_timestamp = self._get_current_timestamp_str(stream_info)
        camera_info = self.get_camera_info_from_stream(stream_info)

        self._ascending_alert_list = self._ascending_alert_list[-900:] if len(self._ascending_alert_list) > 900 else self._ascending_alert_list

        if total_detections > 0:
            level = "low"
            intensity = 5.0
            start_timestamp = self._get_start_timestamp_str(stream_info)
            if start_timestamp and self.current_incident_end_timestamp == "N/A":
                self.current_incident_end_timestamp = "Incident still active"
            elif start_timestamp and self.current_incident_end_timestamp == "Incident still active":
                if len(self._ascending_alert_list) >= 15 and sum(self._ascending_alert_list[-15:]) / 15 < 1.5:
                    self.current_incident_end_timestamp = current_timestamp
            elif self.current_incident_end_timestamp != "Incident still active" and self.current_incident_end_timestamp != "N/A":
                self.current_incident_end_timestamp = "N/A"

            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("all", 15)
                intensity = min(10.0, (total_detections / threshold) * 10)
                if intensity >= 9:
                    level = "critical"
                    self._ascending_alert_list.append(3)
                elif intensity >= 7:
                    level = "significant"
                    self._ascending_alert_list.append(2)
                elif intensity >= 5:
                    level = "medium"
                    self._ascending_alert_list.append(1)
                else:
                    level = "low"
                    self._ascending_alert_list.append(0)
            else:
                if total_detections > 30:
                    level = "critical"
                    intensity = 10.0
                    self._ascending_alert_list.append(3)
                elif total_detections > 25:
                    level = "significant"
                    intensity = 9.0
                    self._ascending_alert_list.append(2)
                elif total_detections > 15:
                    level = "medium"
                    intensity = 7.0
                    self._ascending_alert_list.append(1)
                else:
                    level = "low"
                    intensity = min(10.0, total_detections / 3.0)
                    self._ascending_alert_list.append(0)

            human_text_lines = [f"INCIDENTS DETECTED @ {current_timestamp}:"]
            human_text_lines.append(f"\tSeverity Level: {(self.CASE_TYPE, level)}")
            human_text = "\n".join(human_text_lines)

            alert_settings = []
            if config.alert_config and hasattr(config.alert_config, "alert_type"):
                alert_settings.append({
                    "alert_type": getattr(config.alert_config, "alert_type", ["Default"]),
                    "incident_category": self.CASE_TYPE,
                    "threshold_level": config.alert_config.count_thresholds if hasattr(config.alert_config, "count_thresholds") else {},
                    "ascending": True,
                    "settings": {t: v for t, v in zip(
                        getattr(config.alert_config, "alert_type", ["Default"]),
                        getattr(config.alert_config, "alert_value", ["JSON"])
                    )}
                })

            event = self.create_incident(
                incident_id=f"{self.CASE_TYPE}_{str(frame_number)}",
                incident_type=self.CASE_TYPE,
                severity_level=level,
                human_text=human_text,
                camera_info=camera_info,
                alerts=alerts,
                alert_settings=alert_settings,
                start_time=start_timestamp,
                end_time=self.current_incident_end_timestamp,
                level_settings={"low": 1, "medium": 3, "significant": 4, "critical": 7}
            )
            incidents.append(event)
        else:
            self._ascending_alert_list.append(0)
            incidents.append({})

        return incidents

    def _generate_tracking_stats(
        self,
        counting_summary: Dict,
        alerts: List,
        config: FlareAnalysisConfig,
        frame_number: Optional[int] = None,
        stream_info: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        camera_info = self.get_camera_info_from_stream(stream_info)
        tracking_stats = []
        total_detections = counting_summary.get("total_count", 0)
        total_counts_dict = counting_summary.get("total_counts", {})
        per_category_count = counting_summary.get("per_category_count", {})
        color_distribution = counting_summary.get("color_distribution", {})

        current_timestamp = self._get_current_timestamp_str(stream_info, precision=False)
        start_timestamp = self._get_start_timestamp_str(stream_info, precision=False)
        high_precision_start_timestamp = self._get_current_timestamp_str(stream_info, precision=True)
        high_precision_reset_timestamp = self._get_start_timestamp_str(stream_info, precision=True)

        # Build total_counts array
        total_counts = []
        for cat, count in total_counts_dict.items():
            if count > 0:
                total_counts.append({"category": cat, "count": count})

        # Build current_counts array
        current_counts = []
        for cat, count in per_category_count.items():
            if count > 0 or total_detections > 0:
                current_counts.append({"category": cat, "count": count})

        # Prepare detections with color and height
        detections = []
        frame_height = stream_info.get("input_settings", {}).get("height") if stream_info else None
        for det in counting_summary.get("detections", []):
            bbox = det.get("bounding_box", {})
            category = det.get("category", "flare")
            main_color = det.get("main_color", "unknown")
            detection_obj = self.create_detection_object(category, bbox)
            detection_obj["main_color"] = main_color
            if frame_height:
                if config.bbox_format == "auto":
                    bbox_format = "xmin_ymin_xmax_ymax" if "xmin" in bbox else "x_y_width_height"
                else:
                    bbox_format = config.bbox_format
                if bbox_format == "xmin_ymin_xmax_ymax":
                    bbox_height = bbox["ymax"] - bbox["ymin"]
                elif bbox_format == "x_y_width_height":
                    bbox_height = bbox["height"]
                else:
                    bbox_height = 0
                if bbox_height > 0:
                    relative_height = (bbox_height / frame_height) * 100
                    detection_obj["relative_height"] = round(relative_height, 1)
            detections.append(detection_obj)

        # Build alert_settings array
        alert_settings = []
        if config.alert_config and hasattr(config.alert_config, "alert_type"):
            alert_settings.append({
                "alert_type": getattr(config.alert_config, "alert_type", ["Default"]),
                "incident_category": self.CASE_TYPE,
                "threshold_level": config.alert_config.count_thresholds if hasattr(config.alert_config, "count_thresholds") else {},
                "ascending": True,
                "settings": {t: v for t, v in zip(
                    getattr(config.alert_config, "alert_type", ["Default"]),
                    getattr(config.alert_config, "alert_value", ["JSON"])
                )}
            })

        # Generate human_text
        human_text_lines = ["Tracking Statistics:"]
        human_text_lines.append(f"CURRENT FRAME @ {current_timestamp}")
        for cat, count in per_category_count.items():
            colors = color_distribution.get(cat, {})
            color_details = ", ".join([f"{color}: {cnt}" for color, cnt in colors.items()]) if colors else "none"
            human_text_lines.append(f"\t{cat}: {count} ({color_details})")
        if frame_height and total_detections > 0:
            total_relative_height = 0.0
            detection_count = 0
            for det in counting_summary.get("detections", []):
                bbox = det.get("bounding_box", {})
                if config.bbox_format == "auto":
                    bbox_format = "xmin_ymin_xmax_ymax" if "xmin" in bbox else "x_y_width_height"
                else:
                    bbox_format = config.bbox_format
                if bbox_format == "xmin_ymin_xmax_ymax":
                    bbox_height = bbox["ymax"] - bbox["ymin"]
                elif bbox_format == "x_y_width_height":
                    bbox_height = bbox["height"]
                else:
                    continue
                relative_height = (bbox_height / frame_height) * 100
                total_relative_height += relative_height
                detection_count += 1
            if detection_count > 0:
                avg_relative_height = total_relative_height / detection_count
                human_text_lines.append(f"\tAverage Relative Height: {avg_relative_height:.1f}%")
        human_text_lines.append(f"TOTAL SINCE {start_timestamp}")
        for cat, count in total_counts_dict.items():
            if count > 0:
                colors = color_distribution.get(cat, {})
                color_details = ", ".join([f"{color}: {cnt}" for color, cnt in colors.items()]) if colors else "none"
                human_text_lines.append(f"\t{cat}: {count} ({color_details})")
        if alerts:
            for alert in alerts:
                human_text_lines.append(f"Alerts: {alert.get('settings', {})} sent @ {current_timestamp}")
        else:
            human_text_lines.append("Alerts: None")
        human_text = "\n".join(human_text_lines)

        reset_settings = [
            {
                "interval_type": "daily",
                "reset_time": {"value": 9, "time_unit": "hour"}
            }
        ]

        tracking_stat = self.create_tracking_stats(
            total_counts=total_counts,
            current_counts=current_counts,
            detections=detections,
            human_text=human_text,
            camera_info=camera_info,
            alerts=alerts,
            alert_settings=alert_settings,
            reset_settings=reset_settings,
            start_time=high_precision_start_timestamp,
            reset_time=high_precision_reset_timestamp
        )
        tracking_stats.append(tracking_stat)
        return tracking_stats

    def _generate_business_analytics(
        self, counting_summary: Dict, alerts: List, config: FlareAnalysisConfig,
        frame_number: Optional[int] = None, stream_info: Optional[Dict[str, Any]] = None, is_empty=False
    ) -> List[Dict]:
        if is_empty:
            return []
        return []

    def _generate_summary(
        self, summary: Dict, incidents: List, tracking_stats: List, business_analytics: List, alerts: List
    ) -> List[str]:
        lines = {}
        lines["Application Name"] = self.CASE_TYPE
        lines["Application Version"] = self.CASE_VERSION
        if len(incidents) > 0:
            lines["Incidents:"] = f"\n\t{incidents[0].get('human_text', 'No incidents detected')}\n"
        if len(tracking_stats) > 0:
            lines["Tracking Statistics:"] = f"\t{tracking_stats[0].get('human_text', 'No tracking statistics detected')}\n"
        if len(business_analytics) > 0:
            lines["Business Analytics:"] = f"\t{business_analytics[0].get('human_text', 'No business analytics detected')}\n"
        if len(incidents) == 0 and len(tracking_stats) == 0 and len(business_analytics) == 0:
            lines["Summary"] = "No Summary Data"
        return [lines]

    def _get_track_ids_info(self, detections: List) -> Dict[str, Any]:
        frame_track_ids = set()
        for det in detections:
            tid = det.get("track_id")
            if tid is not None:
                frame_track_ids.add(tid)
        total_track_ids = set()
        for s in getattr(self, "_per_category_total_track_ids", {}).values():
            total_track_ids.update(s)
        return {
            "total_count": len(total_track_ids),
            "current_frame_count": len(frame_track_ids),
            "total_unique_track_ids": len(total_track_ids),
            "current_frame_track_ids": list(frame_track_ids),
            "last_update_time": time.time(),
            "total_frames_processed": getattr(self, "_total_frame_counter", 0)
        }

    def _update_tracking_state(self, detections: List):
        if not hasattr(self, "_per_category_total_track_ids"):
            self._per_category_total_track_ids = {cat: set() for cat in self.target_categories}
        self._current_frame_track_ids = {cat: set() for cat in self.target_categories}

        for det in detections:
            cat = det.get("category")
            raw_track_id = det.get("track_id")
            if cat not in self.target_categories or raw_track_id is None:
                continue
            bbox = det.get("bounding_box", det.get("bbox"))
            canonical_id = self._merge_or_register_track(raw_track_id, bbox)
            det["track_id"] = canonical_id
            self._per_category_total_track_ids.setdefault(cat, set()).add(canonical_id)
            self._current_frame_track_ids[cat].add(canonical_id)

    def get_total_counts(self):
        return {cat: len(ids) for cat, ids in getattr(self, "_per_category_total_track_ids", {}).items()}

    def _format_timestamp_for_video(self, timestamp: float) -> str:
        hours = int(timestamp // 3600)
        minutes = int((timestamp % 3600) // 60)
        seconds = timestamp % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.2f}"

    def _format_timestamp_for_stream(self, timestamp: float) -> str:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y:%m:%d %H:%M:%S")

    def _get_current_timestamp_str(self, stream_info: Optional[Dict[str, Any]], precision=False) -> str:
        if not stream_info:
            return "00:00:00.00"
        if precision:
            if stream_info.get("input_settings", {}).get("stream_type", "video_file") == "video_file":
                stream_time_str = stream_info.get("video_timestamp", "")
                return stream_time_str[:8]
            else:
                return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
        if stream_info.get("input_settings", {}).get("stream_type", "video_file") == "video_file":
            stream_time_str = stream_info.get("video_timestamp", "")
            return stream_time_str[:8]
        else:
            stream_time_str = stream_info.get("stream_time", "")
            if stream_time_str:
                try:
                    timestamp_str = stream_time_str.replace(" UTC", "")
                    dt = datetime.strptime(timestamp_str, "%Y-%m-%d-%H:%M:%S.%f")
                    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
                    return self._format_timestamp_for_stream(timestamp)
                except:
                    return self._format_timestamp_for_stream(time.time())
            else:
                return self._format_timestamp_for_stream(time.time())

    def _get_start_timestamp_str(self, stream_info: Optional[Dict[str, Any]], precision=False) -> str:
        if not stream_info:
            return "00:00:00"
        if precision:
            if stream_info.get("input_settings", {}).get("stream_type", "video_file") == "video_file":
                return "00:00:00"
            else:
                return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
        if stream_info.get("input_settings", {}).get("stream_type", "video_file") == "video_file":
            return "00:00:00"
        else:
            if self._tracking_start_time is None:
                stream_time_str = stream_info.get("stream_time", "")
                if stream_time_str:
                    try:
                        timestamp_str = stream_time_str.replace(" UTC", "")
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%d-%H:%M:%S.%f")
                        self._tracking_start_time = dt.replace(tzinfo=timezone.utc).timestamp()
                    except:
                        self._tracking_start_time = time.time()
                else:
                    self._tracking_start_time = time.time()
            dt = datetime.fromtimestamp(self._tracking_start_time, tz=timezone.utc)
            dt = dt.replace(minute=0, second=0, microsecond=0)
            return dt.strftime("%Y:%m:%d %H:%M:%S")

    def _extract_predictions(self, detections: List) -> List[Dict[str, Any]]:
        return [
            {
                "category": det.get("category", "unknown"),
                "confidence": det.get("confidence", 0.0),
                "bounding_box": det.get("bounding_box", {}),
                "main_color": det.get("main_color", "unknown"),
                "major_colors": det.get("major_colors", [])
            }
            for det in detections
        ]

    def _compute_iou(self, box1: Any, box2: Any) -> float:
        def _bbox_to_list(bbox):
            if bbox is None:
                return []
            if isinstance(bbox, list):
                return bbox[:4] if len(bbox) >= 4 else []
            if isinstance(bbox, dict):
                if "xmin" in bbox:
                    return [bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]]
                if "x1" in bbox:
                    return [bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]]
                values = [v for v in bbox.values() if isinstance(v, (int, float))]
                return values[:4] if len(values) >= 4 else []
            return []

        l1 = _bbox_to_list(box1)
        l2 = _bbox_to_list(box2)
        if len(l1) < 4 or len(l2) < 4:
            return 0.0
        x1_min, y1_min, x1_max, y1_max = l1
        x2_min, y2_min, x2_max, y2_max = l2
        x1_min, x1_max = min(x1_min, x1_max), max(x1_min, x1_max)
        y1_min, y1_max = min(y1_min, y1_max), max(y1_min, y1_max)
        x2_min, x2_max = min(x2_min, x2_max), max(x2_min, x2_max)
        y2_min, y2_max = min(y2_min, y2_max), max(y2_min, y2_max)
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        inter_w = max(0.0, inter_x_max - inter_x_min)
        inter_h = max(0.0, inter_y_max - inter_y_min)
        inter_area = inter_w * inter_h
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = area1 + area2 - inter_area
        return (inter_area / union_area) if union_area > 0 else 0.0

    def _merge_or_register_track(self, raw_id: Any, bbox: Any) -> Any:
        if raw_id is None or bbox is None:
            return raw_id
        now = time.time()
        if raw_id in self._track_aliases:
            canonical_id = self._track_aliases[raw_id]
            track_info = self._canonical_tracks.get(canonical_id)
            if track_info is not None:
                track_info["last_bbox"] = bbox
                track_info["last_update"] = now
                track_info["raw_ids"].add(raw_id)
            return canonical_id
        for canonical_id, info in self._canonical_tracks.items():
            if now - info["last_update"] > self._track_merge_time_window:
                continue
            iou = self._compute_iou(bbox, info["last_bbox"])
            if iou >= self._track_merge_iou_threshold:
                self._track_aliases[raw_id] = canonical_id
                info["last_bbox"] = bbox
                info["last_update"] = now
                info["raw_ids"].add(raw_id)
                return canonical_id
        canonical_id = raw_id
        self._track_aliases[raw_id] = canonical_id
        self._canonical_tracks[canonical_id] = {
            "last_bbox": bbox,
            "last_update": now,
            "raw_ids": {raw_id},
        }
        return canonical_id

    def _format_timestamp(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def _get_tracking_start_time(self) -> str:
        if self._tracking_start_time is None:
            return "N/A"
        return self._format_timestamp(self._tracking_start_time)

    def _set_tracking_start_time(self) -> None:
        self._tracking_start_time = time.time()