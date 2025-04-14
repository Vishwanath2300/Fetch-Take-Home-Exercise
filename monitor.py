
import argparse
import concurrent.futures
import json
import math
import re
import time
import threading
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional

import requests
import yaml


class DomainStats:
    def __init__(self):
        self.success = 0
        self.total = 0
        self.lock = threading.Lock()

    def increment_total(self):
        with self.lock:
            self.total += 1

    def increment_success(self):
        with self.lock:
            self.success += 1

# Checking endpoint availability and response time.
class EndpointMonitor:
    def __init__(self, config_file: str):
        self.endpoints = self._load_config(config_file)
        self.stats = {}  # Domain -> DomainStats mapping
        self._initialize_stats()

    def _load_config(self, config_file: str) -> List[Dict]:
        try:
            with open(config_file, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            exit(1)

    def _initialize_stats(self):
        # Initializing stats for all domains.
        for endpoint in self.endpoints:
            domain = self._extract_domain(endpoint['url'])
            if domain not in self.stats:
                self.stats[domain] = DomainStats()

    def _extract_domain(self, url: str) -> str:
        # Extract domain from URL, ignoring port numbers.
        parsed_url = urllib.parse.urlparse(url)
        return parsed_url.netloc.split(':')[0]  # Remove port if present

    def check_health(self, endpoint: Dict):
        # Check health of a single endpoint on by one.
        url = endpoint['url']
        method = endpoint.get('method', 'GET')
        headers = endpoint.get('headers', {})
        body = endpoint.get('body', '')
        
        domain = self._extract_domain(url)
        if domain not in self.stats:
            self.stats[domain] = DomainStats()
        
        self.stats[domain].increment_total()
        
        try:
            # We convert body string to JSON inase if it's a JSON content
            data = None
            if body and 'content-type' in headers and 'json' in headers['content-type'].lower():
                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    data = body
            elif body:
                data = body
            
            # WE make the request with timeout
            start_time = time.time()
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None,
                timeout=0.5  # 500ms timeout is considerd here 
            )
            response_time = time.time() - start_time
            
            # We need to check if response meets criteria (200-299 status code and has ≤500ms response time)
            if 200 <= response.status_code < 300 and response_time <= 0.5:
                print(f"SUCCESS [{endpoint.get('name', url)}] {url} - Status: {response.status_code}, Time: {response_time:.2f}ms")
                self.stats[domain].increment_success()
                
        except requests.exceptions.Timeout:
            print(f"Request to {url} timed out")
        except requests.exceptions.RequestException as e:
            print(f"Request to {url} failed: {e}")
        except Exception as e:
            print(f"Unexpected error checking {url}: {e}")

    def check_all_endpoints(self):
        # WE need to Check all endpoint present in yaml file.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.check_health, self.endpoints)

    def log_results(self):
        # Here we Log current availability results.
        print("\n--- Availability Report at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "---")
        for domain, stat in self.stats.items():
            with stat.lock:
                percentage = int(round(100 * stat.success / stat.total)) if stat.total > 0 else 0
                print(f"{domain} has {percentage}% availability ({stat.success}/{stat.total} successful requests)")
        print("-------------------------")

    def monitor(self):
        """Start monitoring endpoints."""
        print(f"Starting endpoint monitoring for {len(self.endpoints)} endpoints")
        
        try:
            # This is Initial check
            self.check_all_endpoints()
            self.log_results()
            
            # THis is Continuous monitoring
            while True:
                time.sleep(15)  # We Wait for 15 seconds ,we can increase it as per our need.
                self.check_all_endpoints()
                self.log_results()
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")


def main():
    parser = argparse.ArgumentParser(description='Monitor endpoint availability')
    parser.add_argument('config', help='Path to YAML configuration file')
    args = parser.parse_args()
    
    monitor = EndpointMonitor(args.config)
    monitor.monitor()


if __name__ == "__main__":
    main()