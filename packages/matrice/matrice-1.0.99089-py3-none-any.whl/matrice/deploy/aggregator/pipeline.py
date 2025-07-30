import logging
import time
from typing import Dict
from queue import Queue
from matrice.session import Session
from matrice.deploy.aggregator.ingestor import ResultsIngestor 
from matrice.deploy.aggregator.synchronizer import ResultsSynchronizer
from matrice.deploy.aggregator.aggregator import ResultsAggregator
from matrice.deploy.aggregator.publisher import ResultsPublisher
from matrice.deployment.inference_pipeline import InferencePipeline


class ResultsAggregationPipeline:
    """
    Enhanced deployments aggregator that handles multiple streams, synchronizes results,
    and outputs aggregated results to Kafka topics with consistent structure.
    
    This class orchestrates the complete pipeline for collecting, synchronizing, and 
    publishing results from multiple ML model deployments in an inference pipeline,
    ensuring all results follow the same structure as individual deployment results.
    
    Usage Example:
        ```python
        from matrice import Session
        from matrice.deploy.aggregator import ResultsAggregationPipeline
        
        # Initialize session
        session = Session(account_number="...", access_key="...", secret_key="...")
        
        # Create aggregator for an inference pipeline
        aggregator = ResultsAggregationPipeline(session, "your-inference-pipeline-id")
        
        # Setup the aggregation pipeline
        if aggregator.setup_components():
            print(f"Setup complete for {len(aggregator.deployment_ids)} deployments")
            
            # Start streaming and run until keyboard interrupt
            try:
                aggregator.start_streaming()
            except KeyboardInterrupt:
                print("Pipeline stopped by user")
            finally:
                aggregator.cleanup()
        ```
    """
    
    def __init__(self, session: Session, action_record_id: str):
        """
        Initialize the deployments aggregator.
        
        Args:
            session: Session object for authentication
            action_record_id: Action Record ID
        """
        self.session = session
        self.rpc = session.rpc
        self.action_record_id = action_record_id
        url = f"/v1/project/action/{self.action_record_id}/details"
        self.action_doc = self.rpc.get(url)["data"]
        self.action_type = self.action_doc["action"]
        self.job_params = self.action_doc["jobParams"]
        self.action_details = self.action_doc["actionDetails"]

        self.inference_pipeline_id = self.job_params["inference_pipeline_id"]
        self.aggregator_id = self.job_params["aggregator_id"]

        self.inference_pipeline = InferencePipeline(session, pipeline_id=self.inference_pipeline_id)

        # Initialize components
        self.results_ingestor = None
        self.results_synchronizer = None
        self.results_aggregator = None
        self.results_publisher = None

        # Initialize the final results queue
        self.final_results_queue = Queue()

        # Statistics and monitoring
        self.stats = {
            "start_time": None,
            "deployments_created": 0,
            "pipeline_version": "2.0",
            "errors": 0,
            "last_error": None,
            "last_error_time": None,
            "component_status": {
                "ingestor": "not_initialized",
                "synchronizer": "not_initialized",
                "aggregator": "not_initialized",
                "publisher": "not_initialized"
            }
        }
        
        # State management
        self.components_setup = False
        self.is_running = False
        self.deployment_ids = []

        logging.info("Action doc: %s", self.action_doc)
        self.update_status(
            "AGG_ACK",
            "ACK",
            "Action is acknowledged by aggregator",
        )

    def update_status(
        self,
        step_code: str,
        status: str,
        status_description: str,
    ) -> None:
        """Update status of data preparation.

        Args:
            step_code: Code indicating current step
            status: Status of step
            status_description: Description of status
        """
        try:
            logging.info(status_description)
            url = "/v1/actions"
            payload = {
                "_id": self.action_record_id,
                "action": self.action_type,
                "serviceName": self.action_doc["serviceName"],
                "stepCode": step_code,
                "status": status,
                "statusDescription": status_description,
            }

            self.rpc.put(path=url, payload=payload)
        except Exception as exc:
            logging.error(
                "Exception in update_status: %s",
                str(exc),
            )


    def setup_components(self) -> bool:
        """
        Setup all components and initialize the aggregation pipeline.
        
        Returns:
            bool: True if all components initialized successfully, False otherwise
        """
        try:
            self.components_setup = True
            # Get deployment IDs from the inference pipeline
            self.deployment_ids = self.inference_pipeline.deployment_ids
            if not self.deployment_ids:
                self._record_error("No deployment IDs found in inference pipeline")
                return False
            
            self.stats["deployments_created"] = len(self.deployment_ids)
            self.stats["start_time"] = time.time()
            
            # Initialize the results ingestor
            logging.info("Initializing results ingestor...")
            self.results_ingestor = ResultsIngestor(
                deployment_ids=self.deployment_ids,
                session=self.session,
                consumer_timeout=60.0  # 60 seconds timeout
            )
            self.stats["component_status"]["ingestor"] = "initialized"

            # Initialize the results synchronizer with reasonable timeout
            logging.info("Initializing results synchronizer...")
            self.results_synchronizer = ResultsSynchronizer(
                results_queues=self.results_ingestor.results_queues,
                sync_timeout=15.0  # 15 seconds timeout for synchronization
            )
            self.stats["component_status"]["synchronizer"] = "initialized"
            
            # Initialize the results aggregator
            logging.info("Initializing results aggregator...")
            self.results_aggregator = ResultsAggregator(
                synchronized_results_queue=self.results_synchronizer.synchronized_results_queue
            )
            self.stats["component_status"]["aggregator"] = "initialized"
            
            # Initialize the results publisher
            logging.info("Initializing results publisher...")
            self.results_publisher = ResultsPublisher(
                inference_pipeline_id=self.inference_pipeline_id,
                session=self.session,
                final_results_queue=self.results_aggregator.aggregated_results_queue
            )
            self.stats["component_status"]["publisher"] = "initialized"
            
            logging.info(f"Successfully initialized aggregation pipeline for {len(self.deployment_ids)} deployments")
            return True
            
        except Exception as exc:
            self._record_error(f"Failed to setup components: {str(exc)}")
            return False

    def start_streaming(self, block: bool = True) -> bool:
        """
        Start the complete streaming pipeline: ingestion, synchronization, aggregation, and publishing.
        
        Returns:
            bool: True if streaming started successfully, False otherwise
        """
        if not self.components_setup:
            self.setup_components()

        if not self.deployment_ids:
            logging.error("No deployments available. Call setup_components() first.")
            return False
            
        try:
            if self.is_running:
                logging.warning("Streaming is already running")
                return True
            
            self.is_running = True
            
            # Start components in order: ingestor -> synchronizer -> aggregator -> publisher
            
            # Start results ingestion
            logging.info("Starting results ingestion...")
            if not self.results_ingestor.start_streaming():
                self._record_error("Failed to start results ingestion")
                return False
            self.stats["component_status"]["ingestor"] = "running"
            
            # Start results synchronization
            logging.info("Starting results synchronization...")
            if not self.results_synchronizer.start_synchronization():
                self._record_error("Failed to start results synchronization")
                return False
            self.stats["component_status"]["synchronizer"] = "running"
            
            # Start results aggregation
            logging.info("Starting results aggregation...")
            if not self.results_aggregator.start_aggregation():
                self._record_error("Failed to start results aggregation")
                return False
            self.stats["component_status"]["aggregator"] = "running"
            
            # Start results publishing
            logging.info("Starting results publishing...")
            if not self.results_publisher.start_streaming():
                self._record_error("Failed to start results publishing")
                return False
            self.stats["component_status"]["publisher"] = "running"
            
            logging.info("Aggregation pipeline started successfully")
            if block:
                self.start_logging()
            return True
            
        except Exception as exc:
            self._record_error(f"Failed to start streaming: {str(exc)}")
            self.stop_streaming()
            return False

    def start_logging(self, status_interval: int = 30) -> None:
        """
        Start the pipeline logging and run until interrupted.
        Args:
            status_interval: Interval in seconds between status log messages
        """
        try:
            logging.info("=" * 60)
            logging.info("🚀 Aggregation pipeline is running!")
            logging.info(f"📊 Processing results from {len(self.deployment_ids)} deployments")
            logging.info(f"🔗 Inference Pipeline ID: {self.inference_pipeline_id}")
            if self.deployment_ids:
                logging.info(f"🎯 Deployment IDs: {', '.join(self.deployment_ids)}")
            logging.info("💡 Press Ctrl+C to stop the pipeline")
            logging.info("=" * 60)
            
            last_status_time = time.time()
            
            # Main loop - run until interrupted
            while True:
                try:
                    current_time = time.time()
                    
                    # Periodic status logging
                    if current_time - last_status_time >= status_interval:
                        self._log_pipeline_status()
                        last_status_time = current_time
                    
                    # Check pipeline health
                    health = self.get_health_status()
                    if health.get("overall_status") == "unhealthy":
                        logging.error("Pipeline is unhealthy! Issues: %s", health.get("issues", []))
                        # Continue running but log the issue
                    
                    # Sleep for a short time to prevent busy waiting
                    time.sleep(1.0)
                    
                except KeyboardInterrupt:
                    # Re-raise to be caught by outer handler
                    raise
                except Exception as exc:
                    logging.error(f"Error in main pipeline loop: {exc}")
                    # Continue running unless it's a critical error
                    time.sleep(5.0)
            
        except KeyboardInterrupt:
            logging.info("")
            logging.info("🛑 Keyboard interrupt received - stopping pipeline...")
            
        except Exception as exc:
            logging.error(f"Critical error in pipeline: {exc}")
            self._record_error(f"Critical pipeline error: {str(exc)}")
            
        finally:
            # Always cleanup
            try:
                logging.info("🧹 Cleaning up pipeline resources...")
                self.cleanup()
                logging.info("✅ Pipeline stopped successfully")
            except KeyboardInterrupt:
                # Handle second Ctrl+C during cleanup
                logging.warning("⚠️ Second interrupt received during cleanup - forcing exit...")
                try:
                    # Try quick cleanup
                    self.stop_streaming()
                except:
                    pass
                logging.info("✅ Pipeline force-stopped")
            except Exception as exc:
                logging.error(f"Error during cleanup: {exc}")

    def _log_pipeline_status(self):
        """Log current pipeline status and statistics."""
        try:
            stats = self.get_stats()
            health = self.get_health_status()
            
            logging.info("📈 Pipeline Status Report:")
            logging.info(f"   ⏱️  Runtime: {stats.get('runtime_seconds', 0):.1f} seconds")
            logging.info(f"   🔄 Overall Health: {health.get('overall_status', 'unknown')}")
            
            # Component stats
            components = stats.get("components", {})
            
            if "results_ingestor" in components:
                ingestor_stats = components["results_ingestor"]
                logging.info(f"   📥 Results Consumed: {ingestor_stats.get('results_consumed', 0)}")
            
            if "results_synchronizer" in components:
                sync_stats = components["results_synchronizer"]
                logging.info(f"   🔗 Results Synchronized: {sync_stats.get('results_synchronized', 0)}")
                logging.info(f"   ✅ Complete Syncs: {sync_stats.get('complete_syncs', 0)}")
                logging.info(f"   ⚠️  Partial Syncs: {sync_stats.get('partial_syncs', 0)}")
            
            if "results_aggregator" in components:
                agg_stats = components["results_aggregator"]
                logging.info(f"   🎯 Results Aggregated: {agg_stats.get('aggregations_created', 0)}")
            
            if "results_publisher" in components:
                pub_stats = components["results_publisher"]
                logging.info(f"   📤 Messages Published: {pub_stats.get('messages_produced', 0)}")
            
            # Pipeline metrics
            pipeline_metrics = stats.get("pipeline_metrics", {})
            if pipeline_metrics:
                logging.info(f"   🚀 Throughput: {pipeline_metrics.get('throughput', 0):.2f} msg/sec")
                logging.info(f"   📊 Completion Rate: {pipeline_metrics.get('completion_rate', 0):.1%}")
            
            # Health issues
            issues = health.get("issues", [])
            if issues:
                logging.warning(f"   ⚠️  Issues: {', '.join(issues)}")
            
            logging.info("─" * 50)
            
        except Exception as exc:
            logging.error(f"Error logging pipeline status: {exc}")

    def stop_streaming(self):
        """Stop all streaming operations in reverse order."""
        logging.info("Stopping aggregation pipeline...")
        
        if not self.is_running:
            logging.info("Streaming is not running")
            return
            
        self.is_running = False

        # Stop components in reverse order: publisher -> aggregator -> synchronizer -> ingestor
        if self.results_publisher:
            try:
                logging.info("Stopping results publisher...")
                self.results_publisher.stop_streaming()
                self.stats["component_status"]["publisher"] = "stopped"
            except Exception as exc:
                logging.error(f"Error stopping results publisher: {exc}")

        if self.results_aggregator:
            try:
                logging.info("Stopping results aggregator...")
                self.results_aggregator.stop_aggregation()
                self.stats["component_status"]["aggregator"] = "stopped"
            except Exception as exc:
                logging.error(f"Error stopping results aggregator: {exc}")

        if self.results_synchronizer:
            try:
                logging.info("Stopping results synchronizer...")
                self.results_synchronizer.stop_synchronization()
                self.stats["component_status"]["synchronizer"] = "stopped"
            except Exception as exc:
                logging.error(f"Error stopping results synchronization: {exc}")

        if self.results_ingestor:
            try:
                logging.info("Stopping results ingestor...")
                self.results_ingestor.stop_streaming()
                self.stats["component_status"]["ingestor"] = "stopped"
            except Exception as exc:
                logging.error(f"Error stopping results ingestion: {exc}")
        
        logging.info("Aggregation pipeline stopped")

    def get_stats(self) -> Dict:
        """Get current statistics from all components."""
        stats = self.stats.copy()
        if stats["start_time"]:
            stats["runtime_seconds"] = time.time() - stats["start_time"]
        
        # Add component statistics
        stats["components"] = {}
        
        if self.results_ingestor:
            stats["components"]["results_ingestor"] = self.results_ingestor.get_stats()
        
        if self.results_synchronizer:
            stats["components"]["results_synchronizer"] = self.results_synchronizer.get_stats()
        
        if self.results_aggregator:
            stats["components"]["results_aggregator"] = self.results_aggregator.get_stats()
        
        if self.results_publisher:
            stats["components"]["results_publisher"] = self.results_publisher.get_stats()
        
        # Add pipeline-level metrics
        stats["pipeline_metrics"] = self._calculate_pipeline_metrics()
        
        return stats

    def _calculate_pipeline_metrics(self) -> Dict:
        """Calculate pipeline-level performance metrics."""
        metrics = {
            "throughput": 0.0,
            "latency": 0.0,
            "error_rate": 0.0,
            "completion_rate": 0.0,
        }
        
        try:
            # Calculate throughput (messages per second)
            if self.stats["start_time"]:
                runtime = time.time() - self.stats["start_time"]
                if runtime > 0 and self.results_publisher:
                    publisher_stats = self.results_publisher.get_stats()
                    metrics["throughput"] = publisher_stats.get("messages_produced", 0) / runtime
            
            # Calculate completion rate from synchronizer
            if self.results_synchronizer:
                sync_stats = self.results_synchronizer.get_stats()
                total_syncs = sync_stats.get("complete_syncs", 0) + sync_stats.get("partial_syncs", 0)
                if total_syncs > 0:
                    metrics["completion_rate"] = sync_stats.get("complete_syncs", 0) / total_syncs
            
            # Calculate error rate
            total_errors = self.stats["errors"]
            total_processed = 0
            
            if self.results_ingestor:
                ingestor_stats = self.results_ingestor.get_stats()
                total_processed += ingestor_stats.get("results_consumed", 0)
                total_errors += ingestor_stats.get("errors", 0)
            
            if total_processed > 0:
                metrics["error_rate"] = total_errors / total_processed
            
            # Calculate average latency from synchronizer
            if self.results_synchronizer:
                sync_stats = self.results_synchronizer.get_stats()
                metrics["latency"] = sync_stats.get("avg_sync_time", 0.0)
        
        except Exception as exc:
            logging.error(f"Error calculating pipeline metrics: {exc}")
        
        return metrics

    def get_health_status(self) -> Dict:
        """Get health status of all components."""
        health = {
            "overall_status": "healthy",
            "is_running": self.is_running,
            "pipeline_version": self.stats["pipeline_version"],
            "deployment_count": len(self.deployment_ids),
            "components": {},
            "issues": [],
        }
        
        try:
            # Check components health
            if self.results_ingestor:
                health["components"]["results_ingestor"] = self.results_ingestor.get_health_status()
                if health["components"]["results_ingestor"].get("status") != "healthy":
                    health["issues"].append("Results ingestor is not healthy")
            
            if self.results_synchronizer:
                health["components"]["results_synchronizer"] = self.results_synchronizer.get_health_status()
                if health["components"]["results_synchronizer"].get("status") != "healthy":
                    health["issues"].append("Results synchronizer is not healthy")
            
            if self.results_aggregator:
                health["components"]["results_aggregator"] = self.results_aggregator.get_health_status()
                if health["components"]["results_aggregator"].get("status") != "healthy":
                    health["issues"].append("Results aggregator is not healthy")
            
            if self.results_publisher:
                health["components"]["results_publisher"] = self.results_publisher.get_health_status()
                if health["components"]["results_publisher"].get("status") != "healthy":
                    health["issues"].append("Results publisher is not healthy")
            
            # Determine overall status
            if len(health["issues"]) > 0:
                if len(health["issues"]) >= 2:
                    health["overall_status"] = "unhealthy"
                else:
                    health["overall_status"] = "degraded"
                    
        except Exception as exc:
            health["overall_status"] = "unhealthy"
            health["error"] = str(exc)
            health["issues"].append(f"Error checking health: {str(exc)}")
        
        return health

    def get_deployment_info(self) -> Dict:
        """
        Get information about the deployments in this aggregator.
        
        Returns:
            Dict: Deployment information including IDs, count, and status
        """
        return {
            "inference_pipeline_id": self.inference_pipeline_id,
            "deployment_ids": self.deployment_ids,
            "deployment_count": len(self.deployment_ids),
            "pipeline_status": getattr(self.inference_pipeline, 'status', None),
            "aggregator_running": self.is_running,
            "component_status": self.stats["component_status"].copy(),
        }

    def wait_for_ready(self, timeout: int = 300, poll_interval: int = 10) -> bool:
        """
        Wait for the aggregator to be ready and processing results.
        
        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: Time between checks in seconds
            
        Returns:
            bool: True if aggregator is ready, False if timeout
        """
        if not self.is_running:
            logging.warning("Aggregator is not running")
            return False
            
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                health = self.get_health_status()
                
                # Check if all components are healthy
                if health.get("overall_status") == "healthy":
                    # Check if we're receiving and processing results
                    stats = self.get_stats()
                    components = stats.get("components", {})
                    
                    ingestor_stats = components.get("results_ingestor", {})
                    sync_stats = components.get("results_synchronizer", {})
                    
                    # Consider ready if we're consuming and synchronizing results
                    if (ingestor_stats.get("results_consumed", 0) > 0 and 
                        sync_stats.get("results_synchronized", 0) > 0):
                        logging.info("Aggregation pipeline is ready and processing results")
                        return True
                
                logging.debug(f"Waiting for pipeline readiness... Health: {health.get('overall_status')}")
                time.sleep(poll_interval)
                
            except Exception as exc:
                logging.error(f"Error checking aggregator readiness: {exc}")
                time.sleep(poll_interval)
        
        logging.warning(f"Aggregation pipeline not ready after {timeout} seconds")
        return False

    def force_sync_pending_results(self) -> int:
        """
        Force synchronization of all pending results.
        
        Returns:
            int: Number of pending results that were synchronized
        """
        if not self.results_synchronizer:
            logging.warning("Results synchronizer not initialized")
            return 0
            
        return self.results_synchronizer.force_sync_pending()

    def _record_error(self, error_message: str):
        """Record an error with timestamp."""
        logging.error(error_message)
        self.stats["errors"] += 1
        self.stats["last_error"] = error_message
        self.stats["last_error_time"] = time.time()

    def cleanup(self):
        """Clean up all resources."""
        logging.info("Cleaning up aggregation pipeline resources...")
        
        # Stop streaming if running
        if self.is_running:
            self.stop_streaming()
        
        # Cleanup components in reverse order
        if self.results_publisher:
            try:
                self.results_publisher.cleanup() if hasattr(self.results_publisher, 'cleanup') else None
            except Exception as exc:
                logging.error(f"Error cleaning up publisher: {exc}")
        
        if self.results_aggregator:
            try:
                self.results_aggregator.cleanup()
            except Exception as exc:
                logging.error(f"Error cleaning up aggregator: {exc}")
        
        if self.results_synchronizer:
            try:
                self.results_synchronizer.cleanup()
            except Exception as exc:
                logging.error(f"Error cleaning up synchronizer: {exc}")
        
        if self.results_ingestor:
            try:
                self.results_ingestor.cleanup()
            except Exception as exc:
                logging.error(f"Error cleaning up ingestor: {exc}")
        
        # Clear the final results queue
        if self.final_results_queue:
            try:
                while not self.final_results_queue.empty():
                    self.final_results_queue.get_nowait()
            except Exception:
                pass
        
        logging.info("Aggregation pipeline cleanup completed")

