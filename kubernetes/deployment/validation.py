#!/usr/bin/env python3
import os
import sys
import time
import json
import yaml
import requests
from prometheus_api_client import PrometheusConnect

class DeploymentValidator:
    def __init__(self, environment):
        self.environment = environment
        self.prom = PrometheusConnect(url="http://prometheus:9090")
        
        # Load deployment strategy config
        with open("/etc/deployment/strategy.yaml") as f:
            self.config = yaml.safe_load(f)
        
        self.env_config = self.config['environments'][environment]
    
    def validate_health(self):
        """Validate service health based on configured checks"""
        for check in self.env_config['validation']:
            if check['name'] == 'health-check':
                failures = 0
                for _ in range(check['threshold']):
                    try:
                        response = requests.get(
                            f"http://ai-service:8080{check['endpoint']}",
                            timeout=float(check['timeout'].rstrip('s'))
                        )
                        if not response.ok:
                            failures += 1
                    except requests.exceptions.RequestException:
                        failures += 1
                    time.sleep(float(check['interval'].rstrip('s')))
                
                if failures >= check['threshold']:
                    return False
        return True
    
    def validate_metrics(self):
        """Validate service metrics against thresholds"""
        for check in self.env_config['validation']:
            if check['name'] == 'metrics-check':
                result = self.prom.custom_query(check['query'])
                if result and float(result[0]['value'][1]) > check['threshold']:
                    return False
        return True
    
    def validate_performance(self):
        """Validate performance metrics for production"""
        if self.environment == 'production':
            for check in self.env_config['promotion']:
                if check['name'] == 'performance-check':
                    # Check latency
                    latency = self.prom.custom_query(
                        'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))'
                    )
                    if latency and float(latency[0]['value'][1]) > float(check['latency_p95'].rstrip('ms'))/1000:
                        return False
                    
                    # Check error rate
                    errors = self.prom.custom_query(
                        'sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))'
                    )
                    if errors and float(errors[0]['value'][1]) > check['error_rate']:
                        return False
        return True
    
    def run_validation(self):
        """Run all validation checks"""
        print(f"Starting validation for {self.environment} environment")
        
        checks = {
            "health": self.validate_health(),
            "metrics": self.validate_metrics(),
            "performance": self.validate_performance()
        }
        
        print(f"Validation results: {json.dumps(checks, indent=2)}")
        return all(checks.values())

def main():
    if len(sys.argv) != 2:
        print("Usage: validation.py <environment>")
        sys.exit(1)
    
    environment = sys.argv[1]
    validator = DeploymentValidator(environment)
    
    if not validator.run_validation():
        print("Validation failed")
        sys.exit(1)
    
    print("Validation successful")

if __name__ == "__main__":
    main()
