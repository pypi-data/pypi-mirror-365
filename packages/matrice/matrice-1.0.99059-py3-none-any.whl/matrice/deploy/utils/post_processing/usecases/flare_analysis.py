from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import time
import cv2
import numpy as np
from collections import defaultdict
import tempfile
import os

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
    confidence_threshold: float = 0.5
    top_k_colors: int = 3
    frame_skip: int = 1
    target_categories: List[str] = field(default_factory=lambda: ["BadFlare", "GoodFlare"])
    fps: Optional[float] = None
    bbox_format: str = "auto"
    index_to_category: Dict[int, str] = field(default_factory=lambda: {0: 'BadFlare', 1: 'GoodFlare'})
    alert_config: Optional[AlertConfig] = None
    time_window_minutes: int = 60
    enable_unique_counting: bool = True
    enable_smoothing: bool = True
    smoothing_algorithm: str = "observability"
    smoothing_window_size: int = 20
    smoothing_cooldown_frames: int = 5
    smoothing_confidence_range_factor: float = 0.5

    def validate(self) -> List[str]:
        errors = super().validate()
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            errors.append("confidence_threshold must be between 0 and 1")
        if self.top_k_colors <= 0:
            errors.append("top_k_colors must be positive")
        if self.frame_skip <= 0:
            errors.append("frame_skip must be positive")
        if self.bbox_format not in ["auto", "xmin_ymin_xmax_ymax", "x_y_width_height"]:
            errors.append("bbox_format must be one of: auto, xmin_ymin_xmax_ymax, x_y_width_height")
        if self.smoothing_window_size <= 0:
            errors.append("smoothing_window_size must be positive")
        if self.smoothing_cooldown_frames < 0:
            errors.append("smoothing_cooldown_frames cannot be negative")
        if self.smoothing_confidence_range_factor <= 0:
            errors.append("smoothing_confidence_range_factor must be positive")
        return errors

class FlareAnalysisUseCase(BaseProcessor):
    """Flare analysis processor for detecting and analyzing flare colors in video streams."""
    CATEGORY_DISPLAY = {
        "BadFlare": "Bad Flare",
        "GoodFlare": "Good Flare"
    }
    
    def __init__(self):
        super().__init__("flare_analysis")
        self.category = "flare_detection"
        self.CASE_TYPE: Optional[str] = 'flare_detection'
        self.CASE_VERSION: Optional[str] = '1.3'
        self.target_categories = ["BadFlare", "GoodFlare"]
        self.tracker = None
        self.smoothing_tracker = None
        self._total_frame_counter = 0
        self._global_frame_offset = 0
        self._tracking_start_time = None
        self._track_aliases: Dict[Any, Any] = {}
        self._canonical_tracks: Dict[Any, Dict[str, Any]] = {}
        self._track_merge_iou_threshold: float = 0.05
        self._track_merge_time_window: float = 7.0
        self._ascending_alert_list: List[int] = []
        self.current_incident_end_timestamp: str = "N/A"
        self._flare_total_track_ids = {}
        self._flare_current_frame_track_ids = {}

    def reset_tracker(self) -> None:
        if self.tracker is not None:
            self.tracker.reset()
            self.logger.info("AdvancedTracker reset for new flare analysis session")

    def reset_flare_tracking(self) -> None:
        self._flare_total_track_ids = {}
        self._flare_current_frame_track_ids = {}
        self._total_frame_counter = 0
        self._global_frame_offset = 0
        self._tracking_start_time = None
        self._track_aliases = {}
        self._canonical_tracks = {}
        self._ascending_alert_list = []
        self.current_incident_end_timestamp = "N/A"
        self.logger.info("Flare tracking state reset")

    def reset_all_tracking(self) -> None:
        self.reset_tracker()
        self.reset_flare_tracking()
        self.logger.info("All flare tracking state reset")

    def _compute_iou(self, box1: Any, box2: Any) -> float:
        def _bbox_to_list(bbox):
            if bbox is None:
                return []
            if isinstance(bbox, dict):
                if "xmin" in bbox:
                    return [bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]]
                if "x" in bbox:
                    return [bbox["x"], bbox["y"], bbox["x"] + bbox["width"], bbox["y"] + bbox["height"]]
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

    def _update_flare_tracking_state(self, detections: List[Dict]):
        self._flare_total_track_ids = getattr(self, '_flare_total_track_ids', defaultdict(set))
        self._flare_current_frame_track_ids = defaultdict(set)
        for det in detections:
            cat = det.get('category')
            color = det.get('main_color')
            track_id = det.get('track_id')
            if cat and color and track_id is not None:
                key = f"{cat}:{color}"
                self._flare_total_track_ids[key].add(track_id)
                self._flare_current_frame_track_ids[key].add(track_id)

    def get_total_flare_counts(self):
        return {key: len(ids) for key, ids in getattr(self, '_flare_total_track_ids', {}).items()}

    def _format_timestamp_for_video(self, timestamp: float) -> str:
        hours = int(timestamp // 3600)
        minutes = int((timestamp % 3600) // 60)
        seconds = timestamp % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.2f}"

    def _format_timestamp_for_stream(self, timestamp: float) -> str:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime('%Y:%m:%d %H:%M:%S')

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
            return dt.strftime('%Y:%m:%d %H:%M:%S')

    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "confidence_threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5},
                "top_k_colors": {"type": "integer", "minimum": 1, "default": 3},
                "frame_skip": {"type": "integer", "minimum": 1, "default": 1},
                "target_categories": {"type": ["array", "null"], "items": {"type": "string"}, "default": ["BadFlare", "GoodFlare"]},
                "fps": {"type": ["number", "null"], "minimum": 1.0, "default": None},
                "bbox_format": {"type": "string", "enum": ["auto", "xmin_ymin_xmax_ymax", "x_y_width_height"], "default": "auto"},
                "index_to_category": {"type": ["object", "null"], "default": {0: 'BadFlare', 1: 'GoodFlare'}},
                "alert_config": {"type": ["object", "null"], "default": None},
                "time_window_minutes": {"type": "integer", "minimum": 1, "default": 60},
                "enable_unique_counting": {"type": "boolean", "default": True},
                "enable_smoothing": {"type": "boolean", "default": True},
                "smoothing_algorithm": {"type": "string", "default": "observability"},
                "smoothing_window_size": {"type": "integer", "minimum": 1, "default": 20},
                "smoothing_cooldown_frames": {"type": "integer", "minimum": 0, "default": 5},
                "smoothing_confidence_range_factor": {"type": "number", "minimum": 0, "default": 0.5}
            },
            "required": ["confidence_threshold", "top_k_colors"],
            "additionalProperties": False
        }

    def create_default_config(self, **overrides) -> FlareAnalysisConfig:
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "confidence_threshold": 0.5,
            "top_k_colors": 3,
            "frame_skip": 1,
            "target_categories": ["BadFlare", "GoodFlare"],
            "fps": None,
            "bbox_format": "auto",
            "index_to_category": {0: 'BadFlare', 1: 'GoodFlare'},
            "alert_config": None,
            "time_window_minutes": 60,
            "enable_unique_counting": True,
            "enable_smoothing": True,
            "smoothing_algorithm": "observability",
            "smoothing_window_size": 20,
            "smoothing_cooldown_frames": 5,
            "smoothing_confidence_range_factor": 0.5
        }
        defaults.update(overrides)
        return FlareAnalysisConfig(**defaults)

    def process(
        self,
        data: Any,
        config: ConfigProtocol,
        input_bytes: Optional[bytes] = None,
        context: Optional[ProcessingContext] = None,
        stream_info: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        start_time = time.time()
        if not isinstance(config, FlareAnalysisConfig):
            return self.create_error_result(
                "Invalid configuration type for flare analysis",
                usecase=self.name,
                category=self.category,
                context=context
            )
        if context is None:
            context = ProcessingContext()
        if not input_bytes:
            return self.create_error_result(
                "input_bytes (video/image) is required for flare analysis",
                usecase=self.name,
                category=self.category,
                context=context
            )
        if not data:
            return self.create_error_result(
                "Detection data is required for flare analysis",
                usecase=self.name,
                category=self.category,
                context=context
            )

        input_format = match_results_structure(data)
        context.input_format = input_format
        context.confidence_threshold = config.confidence_threshold
        self.logger.info(f"Processing flare analysis with format: {input_format.value}")

        processed_data = filter_by_confidence(data, config.confidence_threshold)
        if config.index_to_category:
            processed_data = apply_category_mapping(processed_data, config.index_to_category)
        flare_processed_data = filter_by_categories(processed_data.copy(), config.target_categories)

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
            flare_processed_data = bbox_smoothing(flare_processed_data, self.smoothing_tracker.config, self.smoothing_tracker)

        try:
            from ..advanced_tracker import AdvancedTracker
            from ..advanced_tracker.config import TrackerConfig
            if self.tracker is None:
                tracker_config = TrackerConfig()
                self.tracker = AdvancedTracker(tracker_config)
                self.logger.info("Initialized AdvancedTracker for flare analysis tracking")
            flare_processed_data = self.tracker.update(flare_processed_data)
        except Exception as e:
            self.logger.warning(f"AdvancedTracker failed: {e}")

        self._update_flare_tracking_state(flare_processed_data)
        self._total_frame_counter += 1

        frame_number = None
        if stream_info:
            input_settings = stream_info.get("input_settings", {})
            start_frame = input_settings.get("start_frame")
            end_frame = input_settings.get("end_frame")
            if start_frame is not None and end_frame is not None and start_frame == end_frame:
                frame_number = start_frame

        flare_analysis = self._analyze_flares_in_media(flare_processed_data, input_bytes, config)
        flare_summary = self._calculate_flare_summary(flare_analysis, config)
        flare_summary['total_flare_counts'] = self.get_total_flare_counts()
        general_summary = self._calculate_general_summary(processed_data, config)
        insights = self._generate_insights(flare_summary, config)
        alerts = self._check_alerts(flare_summary, frame_number, config)
        metrics = self._calculate_metrics(flare_analysis, flare_summary, config, context)
        predictions = self._extract_predictions(flare_analysis)
        summary = self._generate_summary(flare_summary, general_summary, alerts)
        incidents_list = self._generate_incidents(flare_summary, alerts, config, frame_number, stream_info)
        tracking_stats_list = self._generate_tracking_stats(flare_summary, insights, summary, config, frame_number, stream_info)
        business_analytics_list = self._generate_business_analytics(flare_summary, alerts, config, stream_info, is_empty=True)
        summary_list = self._generate_summary_list(flare_summary, incidents_list, tracking_stats_list, business_analytics_list, alerts)

        incidents = incidents_list[0] if incidents_list else {}
        tracking_stats = tracking_stats_list[0] if tracking_stats_list else {}
        business_analytics = business_analytics_list[0] if business_analytics_list else {}
        summary = summary_list[0] if summary_list else {}
        agg_summary = {str(frame_number) if frame_number is not None else "current_frame": {
            "incidents": incidents,
            "tracking_stats": tracking_stats,
            "business_analytics": business_analytics,
            "alerts": alerts,
            "human_text": summary
        }}

        context.mark_completed()
        result = self.create_result(
            data={
                "agg_summary": agg_summary,
                "flare_analysis": flare_analysis,
                "flare_summary": flare_summary,
                "general_summary": general_summary,
                "alerts": alerts,
                "total_detections": len(flare_analysis),
                "unique_colors": len(flare_summary.get("color_distribution", {})),
            },
            usecase=self.name,
            category=self.category,
            context=context
        )
        result.summary = summary
        result.insights = insights
        result.metrics = metrics
        result.predictions = predictions
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

    def _calculate_flare_summary(self, flare_analysis: List[Dict], config: FlareAnalysisConfig) -> Dict[str, Any]:
        category_colors = defaultdict(lambda: defaultdict(int))
        total_detections = len(flare_analysis)
        detections = []
        for record in flare_analysis:
            category = record["category"]
            main_color = record["main_color"]
            category_colors[category][main_color] += 1
            detections.append({
                "bounding_box": record["bbox"],
                "category": record["category"],
                "confidence": record["confidence"],
                "track_id": record["track_id"],
                "frame_id": record["frame_id"],
                "main_color": record["main_color"]
            })
        summary = {
            "total_detections": total_detections,
            "categories": dict(category_colors),
            "color_distribution": {},
            "dominant_colors": {},
            "detections": detections
        }
        all_colors = defaultdict(int)
        for category_data in category_colors.values():
            for color, count in category_data.items():
                all_colors[color] += count
        summary["color_distribution"] = dict(all_colors)
        for category, colors in category_colors.items():
            if colors:
                dominant_color = max(colors.items(), key=lambda x: x[1])
                summary["dominant_colors"][category] = {
                    "color": dominant_color[0],
                    "count": dominant_color[1],
                    "percentage": round((dominant_color[1] / sum(colors.values())) * 100, 1)
                }
        return summary

    def _calculate_general_summary(self, processed_data: Any, config: FlareAnalysisConfig) -> Dict[str, Any]:
        category_counts = defaultdict(int)
        total_objects = 0
        if isinstance(processed_data, dict):
            for frame_data in processed_data.values():
                if isinstance(frame_data, list):
                    for detection in frame_data:
                        if detection.get("confidence", 1.0) >= config.confidence_threshold:
                            category = detection.get("category", "unknown")
                            category_counts[category] += 1
                            total_objects += 1
        elif isinstance(processed_data, list):
            for detection in processed_data:
                if detection.get("confidence", 1.0) >= config.confidence_threshold:
                    category = detection.get("category", "unknown")
                    category_counts[category] += 1
                    total_objects += 1
        return {
            "total_objects": total_objects,
            "category_counts": dict(category_counts),
            "categories_detected": list(category_counts.keys())
        }

    def _generate_insights(self, flare_summary: Dict, config: FlareAnalysisConfig) -> List[str]:
        insights = []
        total_detections = flare_summary.get("total_detections", 0)
        if total_detections == 0:
            insights.append("No flares detected for color analysis.")
            return insights
        categories = flare_summary.get("categories", {})
        dominant_colors = flare_summary.get("dominant_colors", {})
        color_distribution = flare_summary.get("color_distribution", {})
        for category, colors in categories.items():
            total = sum(colors.values())
            color_details = ", ".join([f"{color}: {count}" for color, count in colors.items()])
            insights.append(f"{category.capitalize()} color[s]: {color_details} (Total: {total})")
        for category, info in dominant_colors.items():
            insights.append(
                f"{category.capitalize()} is mostly {info['color']} "
                f"({info['count']} detections, {info['percentage']}%)"
            )
        unique_colors = len(color_distribution)
        if unique_colors > 1:
            insights.append(f"Detected {unique_colors} unique colors across all flare categories.")
        if color_distribution:
            most_common_color = max(color_distribution.items(), key=lambda x: x[1])
            insights.append(
                f"Most common color overall: {most_common_color[0]} ({most_common_color[1]} detections)"
            )
        return insights

    def _check_alerts(self, summary: Dict, frame_number: Any, config: FlareAnalysisConfig) -> List[Dict]:
        def get_trend(data, lookback=900, threshold=0.8):
            window = data[-lookback:] if len(data) >= lookback else data
            if len(window) < 2:
                return True
            increasing = sum(1 for i in range(1, len(window)) if window[i] >= window[i - 1])
            total = len(window) - 1
            return increasing / total >= threshold if total > 0 else True

        alerts = []
        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        if not config.alert_config or not summary.get("detections"):
            return alerts

        total_detections = summary.get("total_detections", 0)
        if config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total_detections >= threshold:
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": f"Total detections ({total_detections}) exceeds threshold ({threshold})",
                        "category": category,
                        "current_count": total_detections,
                        "threshold": threshold,
                        "timestamp": datetime.now().isoformat(),
                        "alert_id": f"alert_{category}_{frame_key}",
                        "incident_category": self.CASE_TYPE,
                        "ascending": get_trend(self._ascending_alert_list, lookback=900, threshold=0.8),
                        "settings": {t: v for t, v in zip(getattr(config.alert_config, 'alert_type', ['Default']) if hasattr(config.alert_config, 'alert_type') else ['Default'],
                                    getattr(config.alert_config, 'alert_value', ['JSON']) if hasattr(config.alert_config, 'alert_value') else ['JSON'])}
                    })
                elif category in summary.get("categories", {}):
                    category_total = sum(summary["categories"][category].values())
                    if category_total >= threshold:
                        alerts.append({
                            "type": "count_threshold",
                            "severity": "warning",
                            "message": f"{category} detections ({category_total}) exceeds threshold ({threshold})",
                            "category": category,
                            "current_count": category_total,
                            "threshold": threshold,
                            "timestamp": datetime.now().isoformat(),
                            "alert_id": f"alert_{category}_{frame_key}",
                            "incident_category": self.CASE_TYPE,
                            "ascending": get_trend(self._ascending_alert_list, lookback=900, threshold=0.8),
                            "settings": {t: v for t, v in zip(getattr(config.alert_config, 'alert_type', ['Default']) if hasattr(config.alert_config, 'alert_type') else ['Default'],
                                        getattr(config.alert_config, 'alert_value', ['JSON']) if hasattr(config.alert_config, 'alert_value') else ['JSON'])}
                        })
        return alerts

    def _calculate_metrics(self, flare_analysis: List[Dict], flare_summary: Dict, config: FlareAnalysisConfig, context: ProcessingContext) -> Dict[str, Any]:
        total_detections = len(flare_analysis)
        unique_colors = len(flare_summary.get("color_distribution", {}))
        metrics = {
            "total_detections": total_detections,
            "unique_colors": unique_colors,
            "categories_analyzed": len(flare_summary.get("categories", {})),
            "processing_time": context.processing_time or 0.0,
            "input_format": context.input_format.value,
            "confidence_threshold": config.confidence_threshold,
            "color_diversity": 0.0,
            "detection_rate": 0.0,
            "average_colors_per_detection": config.top_k_colors
        }
        if total_detections > 0:
            metrics["color_diversity"] = (unique_colors / total_detections) * 100
        if config.time_window_minutes and config.time_window_minutes > 0:
            metrics["detection_rate"] = (total_detections / config.time_window_minutes) * 60
        category_metrics = {}
        for category, colors in flare_summary.get("categories", {}).items():
            category_total = sum(colors.values())
            category_metrics[category] = {
                "count": category_total,
                "unique_colors": len(colors),
                "color_diversity": (len(colors) / category_total) * 100 if category_total > 0 else 0
            }
        metrics["category_metrics"] = category_metrics
        metrics["processing_settings"] = {
            "confidence_threshold": config.confidence_threshold,
            "top_k_colors": config.top_k_colors,
            "frame_skip": config.frame_skip,
            "target_categories": config.target_categories,
            "enable_unique_counting": config.enable_unique_counting
        }
        return metrics

    def _extract_predictions(self, detections: List[Dict]) -> List[Dict[str, Any]]:
        return [{
            "category": det.get("category", "unknown"),
            "confidence": det.get("confidence", 0.0),
            "bounding_box": det.get("bbox", {}),
            "main_color": det.get("main_color", "unknown"),
            "major_colors": det.get("major_colors", [])
        } for det in detections]

    def _generate_summary(self, flare_summary: Dict, general_summary: Dict, alerts: List) -> str:
        total_detections = flare_summary.get("total_detections", 0)
        unique_colors = len(flare_summary.get("color_distribution", {}))
        if total_detections == 0:
            return "No flares detected for color analysis"
        summary_parts = [f"{total_detections} flares analyzed for colors"]
        if unique_colors > 0:
            summary_parts.append(f"{unique_colors} unique colors detected")
        categories = flare_summary.get("categories", {})
        if len(categories) > 1:
            summary_parts.append(f"across {len(categories)} categories")
        if alerts:
            alert_count = len(alerts)
            summary_parts.append(f"with {alert_count} alert{'s' if alert_count != 1 else ''}")
        return ", ".join(summary_parts)

    def _generate_incidents(self, flare_summary: Dict, alerts: List, config: FlareAnalysisConfig, frame_number: Optional[int] = None, stream_info: Optional[Dict[str, Any]] = None) -> List[Dict]:
        incidents = []
        total_detections = flare_summary.get("total_detections", 0)
        current_timestamp = self._get_current_timestamp_str(stream_info)
        camera_info = self.get_camera_info_from_stream(stream_info)
        self._ascending_alert_list = self._ascending_alert_list[-900:] if len(self._ascending_alert_list) > 900 else self._ascending_alert_list
        if total_detections > 0:
            level = "low"
            intensity = 5.0
            start_timestamp = self._get_start_timestamp_str(stream_info)
            if start_timestamp and self.current_incident_end_timestamp == 'N/A':
                self.current_incident_end_timestamp = 'Incident still active'
            elif start_timestamp and self.current_incident_end_timestamp == 'Incident still active':
                if len(self._ascending_alert_list) >= 15 and sum(self._ascending_alert_list[-15:]) / 15 < 1.5:
                    self.current_incident_end_timestamp = current_timestamp
            elif self.current_incident_end_timestamp != 'Incident still active' and self.current_incident_end_timestamp != 'N/A':
                self.current_incident_end_timestamp = 'N/A'
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
                    self._ascending_alert_list.append