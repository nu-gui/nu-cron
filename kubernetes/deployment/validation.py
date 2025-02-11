#!/usr/bin/env python3
"""Validates deployment health and performance metrics."""

import sys
import time
import json
import yaml
import requests
from prometheus_api_client import PrometheusConnect


class DeploymentValidator:
    """Validates deployment health and performance.

    Handles health checks, metrics validation, and performance monitoring
    across different environments.
    """

    def __init__(self, environment):
        """Initialize validator with environment configuration.

        Args:
            environment: Name of the environment to validate
                (staging, production).
        """
        self.environment = environment
        self.prom = PrometheusConnect(url="http://prometheus:9090")

        # Load deployment strategy config
        with open("/etc/deployment/strategy.yaml") as f:
            self.config = yaml.safe_load(f)

        self.env_config = self.config["environments"][environment]

    def validate_health(self):
        """Validate service health based on configured checks.

        Returns:
            bool: True if health checks pass, False otherwise.
        """
        for check in self.env_config["validation"]:
            if check["name"] == "health-check":
                failures = 0
                threshold = check["threshold"]
                timeout = float(check["timeout"].rstrip("s"))
                interval = float(check["interval"].rstrip("s"))

                for _ in range(threshold):
                    try:
                        response = requests.get(
                            f"http://ai-service:8080{check['endpoint']}",
                            timeout=timeout,
                        )
                        if not response.ok:
                            failures += 1
                    except requests.exceptions.RequestException:
                        failures += 1
                    time.sleep(interval)

                if failures >= threshold:
                    return False
        return True

    def validate_metrics(self):
        """Validate service metrics against thresholds.

        Returns:
            bool: True if metrics are within thresholds, False otherwise.
        """
        for check in self.env_config["validation"]:
            if check["name"] == "metrics-check":
                result = self.prom.custom_query(check["query"])
                threshold = check["threshold"]
                if result and float(result[0]["value"][1]) > threshold:
                    return False
        return True

    def validate_performance(self):
        """Validate performance metrics for production.

        Returns:
            bool: True if performance metrics are within thresholds,
                 False otherwise.
        """
        if self.environment == "production":
            for check in self.env_config["promotion"]:
                if check["name"] == "performance-check":
                    # Check latency
                    # Check latency
                    # Build latency query
                    metric = "http_request_duration_seconds_bucket"
                    # Build query parts
                    metric_rate = f"rate({metric}[5m])"
                    latency_query = (
                        "histogram_quantile(0.95, "
                        f"sum({metric_rate}) by (le))"
                    )
                    latency = self.prom.custom_query(latency_query)
                    # Convert ms to seconds for threshold
                    ms_threshold = check["latency_p95"].rstrip("ms")
                    latency_threshold = float(ms_threshold) / 1000

                    # Extract latency value and compare
                    latency_value = float(latency[0]["value"][1])
                    if latency and latency_value > latency_threshold:
                        return False

                    # Check error rate
                    error_query = (
                        'sum(rate(http_requests_total{status=~"5.."}[5m])) / '
                        "sum(rate(http_requests_total[5m]))"
                    )
                    errors = self.prom.custom_query(error_query)
                    error_rate = float(errors[0]["value"][1])
                    if errors and error_rate > check["error_rate"]:
                        return False
        return True

    def run_validation(self):
        """Run all validation checks.

        Returns:
            bool: True if all validation checks pass, False otherwise.
        """
        print(f"Starting validation for {self.environment} environment")

        # Run all validation checks
        checks = {
            "health": self.validate_health(),
            "metrics": self.validate_metrics(),
            "performance": self.validate_performance(),
        }

        # Print results and return overall status
        print(f"Validation results: {json.dumps(checks, indent=2)}")
        return all(checks.values())


def main():
    """Entry point for validation script."""
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
