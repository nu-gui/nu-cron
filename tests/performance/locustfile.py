"""Performance test suite for AI service endpoints."""

from locust import HttpUser, task, between


class AIServiceUser(HttpUser):
    """User class for load testing AI service endpoints."""

    wait_time = between(1, 3)

    @task(3)
    def health_check(self):
        """Test health check endpoint."""
        self.client.get("/health")

    @task(2)
    def metrics_check(self):
        """Test metrics endpoint."""
        self.client.get("/metrics")

    @task(1)
    def api_check(self):
        """Test analyze API endpoint."""
        self.client.post(
            "/api/v1/analyze",
            json={"task": "test_task", "parameters": {"test": "value"}},
        )

    def on_start(self):
        """Setup authentication if needed."""
        pass  # Add auth setup if required
