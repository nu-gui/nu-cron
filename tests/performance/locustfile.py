from locust import HttpUser, task, between

class AIServiceUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def health_check(self):
        self.client.get("/health")
    
    @task(2)
    def metrics_check(self):
        self.client.get("/metrics")
    
    @task(1)
    def api_check(self):
        self.client.post("/api/v1/analyze", json={
            "task": "test_task",
            "parameters": {
                "test": "value"
            }
        })

    def on_start(self):
        """Setup authentication if needed"""
        pass  # Add auth setup if required
