#!/usr/bin/env python3

from typing import Dict, Any, Optional
import logging
import os
import yaml
import subprocess
import argparse

from ...core.config import Settings
from ...models.database import Environment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvironmentManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def create_environment(self, env_name: str, env_type: str) -> bool:
        """Create a new development environment"""
        try:
            if env_type == "docker":
                return self._create_docker_environment(env_name)
            elif env_type == "kubernetes":
                return self._create_kubernetes_environment(env_name)
            else:
                logger.error(f"Unsupported environment type: {env_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to create environment: {e}")
            return False

    def _create_docker_environment(self, env_name: str) -> bool:
        """Create Docker-based environment"""
        try:
            env_config = self.config['environments']['docker'][env_name]
            compose_file = env_config['compose_file']
            
            # Create environment directory
            os.makedirs(f"environments/{env_name}", exist_ok=True)
            
            # Start Docker Compose environment
            cmd = f"docker-compose -f {compose_file} -p {env_name} up -d"
            subprocess.run(cmd, shell=True, check=True)
            
            # Configure monitoring
            self._setup_monitoring(env_name, "docker")
            
            logger.info(f"Docker environment '{env_name}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create Docker environment: {e}")
            return False

    def _create_kubernetes_environment(self, env_name: str) -> bool:
        """Create Kubernetes-based environment"""
        try:
            env_config = self.config['environments']['kubernetes'][env_name]
            namespace = env_config['namespace']
            
            # Create namespace
            cmd = f"kubectl create namespace {namespace}"
            subprocess.run(cmd, shell=True, check=True)
            
            # Apply resource quotas
            quota_spec = {
                "apiVersion": "v1",
                "kind": "ResourceQuota",
                "metadata": {"name": f"{namespace}-quota"},
                "spec": {
                    "hard": {
                        "cpu": env_config['resources']['cpu'],
                        "memory": env_config['resources']['memory']
                    }
                }
            }
            
            with open(f"environments/{namespace}-quota.yaml", 'w') as f:
                yaml.dump(quota_spec, f)
            
            cmd = f"kubectl apply -f environments/{namespace}-quota.yaml -n {namespace}"
            subprocess.run(cmd, shell=True, check=True)
            
            # Deploy services
            for service in env_config['services']:
                cmd = f"kubectl apply -f {service} -n {namespace}"
                subprocess.run(cmd, shell=True, check=True)
            
            # Configure monitoring
            self._setup_monitoring(env_name, "kubernetes")
            
            logger.info(f"Kubernetes environment '{env_name}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create Kubernetes environment: {e}")
            return False

    def _setup_monitoring(self, env_name: str, env_type: str) -> None:
        """Configure monitoring for the environment"""
        try:
            monitoring_config = self.config['monitoring']
            
            if env_type == "docker":
                # Configure Prometheus for Docker environment
                prometheus_config = {
                    "global": {
                        "scrape_interval": "15s"
                    },
                    "scrape_configs": [
                        {
                            "job_name": f"{env_name}-monitoring",
                            "static_configs": [
                                {"targets": [f"{env_name}:9090"]}
                            ]
                        }
                    ]
                }
                
                with open(f"environments/{env_name}/prometheus.yml", 'w') as f:
                    yaml.dump(prometheus_config, f)
                
            elif env_type == "kubernetes":
                # Deploy Prometheus Operator
                cmd = f"helm install prometheus prometheus-community/kube-prometheus-stack --namespace {env_name}"
                subprocess.run(cmd, shell=True, check=True)
                
            logger.info(f"Monitoring configured for environment '{env_name}'")
        except Exception as e:
            logger.error(f"Failed to setup monitoring: {e}")

    def destroy_environment(self, env_name: str, env_type: str) -> bool:
        """Destroy a development environment"""
        try:
            if env_type == "docker":
                cmd = f"docker-compose -p {env_name} down -v"
                subprocess.run(cmd, shell=True, check=True)
            elif env_type == "kubernetes":
                namespace = self.config['environments']['kubernetes'][env_name]['namespace']
                cmd = f"kubectl delete namespace {namespace}"
                subprocess.run(cmd, shell=True, check=True)
            
            logger.info(f"Environment '{env_name}' destroyed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to destroy environment: {e}")
            return False

    def scale_environment(self, env_name: str, service: str, replicas: int) -> bool:
        """Scale services in an environment"""
        try:
            env_config = self.config['environments']['kubernetes'][env_name]
            namespace = env_config['namespace']
            
            cmd = f"kubectl scale deployment {service} --replicas={replicas} -n {namespace}"
            subprocess.run(cmd, shell=True, check=True)
            
            logger.info(f"Scaled service '{service}' to {replicas} replicas")
            return True
        except Exception as e:
            logger.error(f"Failed to scale environment: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Manage development environments")
    parser.add_argument("action", choices=["create", "destroy", "scale"])
    parser.add_argument("--env-name", required=True, help="Environment name")
    parser.add_argument("--env-type", choices=["docker", "kubernetes"], required=True)
    parser.add_argument("--service", help="Service name for scaling")
    parser.add_argument("--replicas", type=int, help="Number of replicas for scaling")
    parser.add_argument("--config", default="devin/settings/ai_config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    manager = EnvironmentManager(args.config)
    
    if args.action == "create":
        success = manager.create_environment(args.env_name, args.env_type)
    elif args.action == "destroy":
        success = manager.destroy_environment(args.env_name, args.env_type)
    elif args.action == "scale":
        if not args.service or not args.replicas:
            logger.error("Service and replicas required for scaling")
            return
        success = manager.scale_environment(args.env_name, args.service, args.replicas)
    
    if not success:
        logger.error("Operation failed")

if __name__ == "__main__":
    main()
