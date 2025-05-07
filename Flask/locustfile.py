import os
import csv
from datetime import datetime
import random
from locust import HttpUser, task, between, events
from typing import List, Dict

class PerformanceMetricsCollector:
    def __init__(self):
        """
        Initialize performance metrics collector
        """
        self.metrics: List[Dict] = []
        self.start_time = datetime.now()
        
        # Ensure results directory exists
        os.makedirs('performance_results', exist_ok=True)

    def add_metric(self, 
                   request_type: str, 
                   name: str, 
                   response_time: float, 
                   response_length: int, 
                   response_code: int, 
                   concurrent_users: int,
                   success: bool):
        """
        Add performance metric to collection
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'request_type': request_type,
            'name': name,
            'response_time': response_time,
            'response_length': response_length,
            'response_code': response_code,
            'concurrent_users': concurrent_users,
            'success': success
        }
        self.metrics.append(metric)

    def save_results(self):
        """
        Save performance metrics to CSV
        """
        if not self.metrics:
            print("No metrics to save.")
            return

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'performance_results/performance_metrics_{timestamp}.csv'

        try:
            with open(filename, 'w', newline='') as csvfile:
                # Use first metric's keys as fieldnames
                fieldnames = self.metrics[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write all metrics
                for metric in self.metrics:
                    writer.writerow(metric)

            print(f"Performance metrics saved to {filename}")
            
            # Calculate and print summary
            self._print_summary()

        except Exception as e:
            print(f"Error saving performance metrics: {e}")

    def _print_summary(self):
        """
        Print performance test summary
        """
        # Response Time Analysis
        response_times = [m['response_time'] for m in self.metrics]
        successful_requests = [m for m in self.metrics if m['success']]
        
        print("\n--- Performance Test Summary ---")
        print(f"Total Requests: {len(self.metrics)}")
        print(f"Successful Requests: {len(successful_requests)}")
        print(f"Failed Requests: {len(self.metrics) - len(successful_requests)}")
        
        print("\nResponse Time Metrics:")
        print(f"Average Response Time: {sum(response_times) / len(response_times):.2f} ms")
        print(f"Minimum Response Time: {min(response_times):.2f} ms")
        print(f"Maximum Response Time: {max(response_times):.2f} ms")

        # Throughput Calculation
        test_duration = (datetime.now() - self.start_time).total_seconds()
        throughput = len(self.metrics) / test_duration
        print(f"\nThroughput: {throughput:.2f} requests/second")

# Global performance metrics collector
performance_collector = PerformanceMetricsCollector()

# Locust event listeners
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Save results when test stops
    """
    performance_collector.save_results()

class TodoLoadTest(HttpUser):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.todo_ids = []
    
    @task(3)
    def get_todos(self):
        """
        Get all todos
        """
        start_time = datetime.now()
        
        with self.client.get("/todos", catch_response=True) as response:
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Record performance metric
            performance_collector.add_metric(
                request_type='GET',
                name='/todos',
                response_time=response_time,
                response_length = len(response.content) if response and response.content else 0,
                response_code=response.status_code,
                concurrent_users=self.environment.runner.user_count,
                success=response.status_code in [200, 204]  # Support both frameworks
            )
    
    @task(2)
    def create_todo(self):
        """
        Create a new todo
        """
        start_time = datetime.now()
        
        # Generate todo
        todo = {
            "id": random.randint(1, 10000),
            "item": f"Test Todo {random.randint(1, 1000)}",
            "completed": False
        }
        
        with self.client.post(
            "/todos", 
            json=todo, 
            headers={'Content-Type': 'application/json'},
            catch_response=True
        ) as response:
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Record performance metric
            performance_collector.add_metric(
                request_type='POST',
                name='/todos',
                response_time=response_time,
                response_length = len(response.content) if response and response.content else 0,
                response_code=response.status_code,
                concurrent_users=self.environment.runner.user_count,
                success=response.status_code in [200, 201]  # Support both frameworks
            )
            
            # Store todo ID if successful
            if response.status_code in [200, 201]:
                self.todo_ids.append(todo['id'])
    
    @task(1)
    def update_todo(self):
        """
        Update an existing todo
        """
        if not self.todo_ids:
            return
        
        start_time = datetime.now()
        
        # Select a random todo
        todo_id = random.choice(self.todo_ids)
        updated_todo = {
            "id": todo_id,
            "item": f"Updated Todo {random.randint(1, 1000)}",
            "completed": random.choice([True, False])
        }
        
        with self.client.put(
            f"/todos/{todo_id}", 
            json=updated_todo, 
            headers={'Content-Type': 'application/json'},
            catch_response=True
        ) as response:
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Record performance metric
            performance_collector.add_metric(
                request_type='PUT',
                name=f'/todos/{todo_id}',
                response_time=response_time,
                response_length = len(response.content) if response and response.content else 0,
                response_code=response.status_code,
                concurrent_users=self.environment.runner.user_count,
                success=response.status_code in [200, 204]  # Support both frameworks
            )
    
    @task(1)
    def delete_todo(self):
        """
        Delete an existing todo
        """
        if not self.todo_ids:
            return
        
        start_time = datetime.now()
        
        # Select a random todo
        todo_id = random.choice(self.todo_ids)
        
        with self.client.delete(
            f"/todos/{todo_id}", 
            catch_response=True
        ) as response:
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Record performance metric
            performance_collector.add_metric(
                request_type='DELETE',
                name=f'/todos/{todo_id}',
                response_time=response_time,
                response_length = len(response.content) if response and response.content else 0,
                response_code=response.status_code,
                concurrent_users=self.environment.runner.user_count,
                success=response.status_code in [200, 204]  # Support both frameworks
            )
            
            # Remove todo ID if successful
            if response.status_code in [200, 204]:
                self.todo_ids.remove(todo_id)