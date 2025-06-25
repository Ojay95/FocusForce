#!/usr/bin/env python3
import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Use local server URL for testing
BASE_URL = "http://0.0.0.0:8001/api"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name, passed, message="", response=None):
    """Log test results"""
    status = "✅ PASSED" if passed else "❌ FAILED"
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "message": message,
        "response": response.json() if response and hasattr(response, 'json') else None,
        "status_code": response.status_code if response else None
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    print(f"{status} - {name}")
    if message:
        print(f"  {message}")
    if response:
        try:
            print(f"  Status: {response.status_code}")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"  Response: {response.text}")
    print("-" * 80)

def test_health_check():
    """Test the health check endpoint"""
    print("\n🔍 Testing Health Check Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health")
        passed = response.status_code == 200 and "status" in response.json() and response.json()["status"] == "healthy"
        log_test("Health Check Endpoint", passed, "Health check endpoint should return status 'healthy'", response)
    except Exception as e:
        log_test("Health Check Endpoint", False, f"Exception: {str(e)}")

def test_stats_endpoint():
    """Test the stats endpoint"""
    print("\n🔍 Testing Stats Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        passed = response.status_code == 200 and "total_tasks" in response.json()
        log_test("Stats Endpoint", passed, "Stats endpoint should return task statistics", response)
    except Exception as e:
        log_test("Stats Endpoint", False, f"Exception: {str(e)}")

def test_project_crud():
    """Test project CRUD operations"""
    print("\n🔍 Testing Project CRUD Operations")
    project_id = None
    
    # Create a project
    try:
        project_data = {
            "name": f"Test Project {uuid.uuid4()}",
            "description": "A test project for API testing",
            "color": "#ff5733"
        }
        response = requests.post(f"{BASE_URL}/projects", json=project_data)
        project_id = response.json().get("id")
        passed = response.status_code == 200 and "id" in response.json() and response.json()["name"] == project_data["name"]
        log_test("Create Project", passed, "Should create a new project", response)
    except Exception as e:
        log_test("Create Project", False, f"Exception: {str(e)}")
        return
    
    # Get all projects
    try:
        response = requests.get(f"{BASE_URL}/projects")
        passed = response.status_code == 200 and isinstance(response.json(), list)
        log_test("Get All Projects", passed, "Should return a list of projects", response)
    except Exception as e:
        log_test("Get All Projects", False, f"Exception: {str(e)}")
    
    # Update project
    if project_id:
        try:
            updated_data = {
                "name": f"Updated Project {uuid.uuid4()}",
                "description": "An updated test project",
                "color": "#33ff57"
            }
            response = requests.put(f"{BASE_URL}/projects/{project_id}", json=updated_data)
            passed = response.status_code == 200 and response.json()["name"] == updated_data["name"]
            log_test("Update Project", passed, "Should update an existing project", response)
        except Exception as e:
            log_test("Update Project", False, f"Exception: {str(e)}")
    
    # Test invalid project update
    try:
        invalid_id = str(uuid.uuid4())
        response = requests.put(f"{BASE_URL}/projects/{invalid_id}", json={"name": "Invalid Project"})
        passed = response.status_code == 404
        log_test("Update Non-existent Project", passed, "Should return 404 for non-existent project", response)
    except Exception as e:
        log_test("Update Non-existent Project", False, f"Exception: {str(e)}")
    
    return project_id

def test_task_crud(project_id=None):
    """Test task CRUD operations"""
    print("\n🔍 Testing Task CRUD Operations")
    task_id = None
    
    # Create a task
    try:
        task_data = {
            "title": f"Test Task {uuid.uuid4()}",
            "description": "A test task for API testing",
            "priority": "high",
            "status": "todo",
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "project_id": project_id
        }
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        task_id = response.json().get("id")
        passed = response.status_code == 200 and "id" in response.json() and response.json()["title"] == task_data["title"]
        log_test("Create Task", passed, "Should create a new task", response)
    except Exception as e:
        log_test("Create Task", False, f"Exception: {str(e)}")
        return
    
    # Get all tasks
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        passed = response.status_code == 200 and isinstance(response.json(), list)
        log_test("Get All Tasks", passed, "Should return a list of tasks", response)
    except Exception as e:
        log_test("Get All Tasks", False, f"Exception: {str(e)}")
    
    # Get tasks by project
    if project_id:
        try:
            response = requests.get(f"{BASE_URL}/tasks?project_id={project_id}")
            passed = response.status_code == 200 and isinstance(response.json(), list)
            log_test("Get Tasks by Project", passed, "Should return tasks for a specific project", response)
        except Exception as e:
            log_test("Get Tasks by Project", False, f"Exception: {str(e)}")
    
    # Update task
    if task_id:
        try:
            updated_data = {
                "title": f"Updated Task {uuid.uuid4()}",
                "description": "An updated test task",
                "priority": "medium",
                "status": "in_progress"
            }
            response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=updated_data)
            passed = response.status_code == 200 and response.json()["title"] == updated_data["title"]
            log_test("Update Task", passed, "Should update an existing task", response)
        except Exception as e:
            log_test("Update Task", False, f"Exception: {str(e)}")
        
        # Update task to completed
        try:
            completed_data = {
                "title": f"Completed Task {uuid.uuid4()}",
                "description": "A completed test task",
                "priority": "low",
                "status": "completed"
            }
            response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=completed_data)
            passed = (response.status_code == 200 and 
                     response.json()["status"] == "completed" and 
                     "completed_at" in response.json() and 
                     response.json()["completed_at"] is not None)
            log_test("Complete Task", passed, "Should mark task as completed and set completed_at", response)
        except Exception as e:
            log_test("Complete Task", False, f"Exception: {str(e)}")
    
    # Test invalid task update
    try:
        invalid_id = str(uuid.uuid4())
        response = requests.put(f"{BASE_URL}/tasks/{invalid_id}", json={"title": "Invalid Task"})
        passed = response.status_code == 404
        log_test("Update Non-existent Task", passed, "Should return 404 for non-existent task", response)
    except Exception as e:
        log_test("Update Non-existent Task", False, f"Exception: {str(e)}")
    
    return task_id

def test_task_deletion(task_id):
    """Test task deletion"""
    print("\n🔍 Testing Task Deletion")
    if not task_id:
        log_test("Delete Task", False, "No task ID provided for deletion test")
        return
    
    try:
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
        passed = response.status_code == 200 and "message" in response.json()
        log_test("Delete Task", passed, "Should delete an existing task", response)
        
        # Verify task is deleted
        response = requests.get(f"{BASE_URL}/tasks")
        task_exists = any(task.get("id") == task_id for task in response.json())
        passed = not task_exists
        log_test("Verify Task Deletion", passed, "Deleted task should not appear in task list")
    except Exception as e:
        log_test("Delete Task", False, f"Exception: {str(e)}")
    
    # Test invalid task deletion
    try:
        invalid_id = str(uuid.uuid4())
        response = requests.delete(f"{BASE_URL}/tasks/{invalid_id}")
        passed = response.status_code == 404
        log_test("Delete Non-existent Task", passed, "Should return 404 for non-existent task", response)
    except Exception as e:
        log_test("Delete Non-existent Task", False, f"Exception: {str(e)}")

def test_project_deletion_cascade(project_id):
    """Test project deletion with cascade to tasks"""
    print("\n🔍 Testing Project Deletion with Cascade")
    if not project_id:
        log_test("Delete Project with Cascade", False, "No project ID provided for deletion test")
        return
    
    # Create tasks for this project
    task_ids = []
    for i in range(2):
        try:
            task_data = {
                "title": f"Cascade Test Task {i} - {uuid.uuid4()}",
                "description": "A test task for cascade deletion testing",
                "priority": "medium",
                "project_id": project_id
            }
            response = requests.post(f"{BASE_URL}/tasks", json=task_data)
            if response.status_code == 200:
                task_ids.append(response.json().get("id"))
        except Exception:
            pass
    
    # Verify tasks were created
    try:
        response = requests.get(f"{BASE_URL}/tasks?project_id={project_id}")
        passed = response.status_code == 200 and len(response.json()) >= len(task_ids)
        log_test("Create Tasks for Cascade Test", passed, f"Created {len(task_ids)} tasks for project", response)
    except Exception as e:
        log_test("Create Tasks for Cascade Test", False, f"Exception: {str(e)}")
        return
    
    # Delete the project
    try:
        response = requests.delete(f"{BASE_URL}/projects/{project_id}")
        passed = response.status_code == 200 and "message" in response.json()
        log_test("Delete Project", passed, "Should delete an existing project", response)
    except Exception as e:
        log_test("Delete Project", False, f"Exception: {str(e)}")
        return
    
    # Verify project is deleted
    try:
        response = requests.get(f"{BASE_URL}/projects")
        project_exists = any(project.get("id") == project_id for project in response.json())
        passed = not project_exists
        log_test("Verify Project Deletion", passed, "Deleted project should not appear in project list")
    except Exception as e:
        log_test("Verify Project Deletion", False, f"Exception: {str(e)}")
    
    # Verify associated tasks are deleted
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        tasks_exist = any(task.get("project_id") == project_id for task in response.json())
        passed = not tasks_exist
        log_test("Verify Cascade Deletion", passed, "Tasks associated with deleted project should be deleted")
    except Exception as e:
        log_test("Verify Cascade Deletion", False, f"Exception: {str(e)}")

def test_motivational_quote():
    """Test the motivational quote endpoint"""
    print("\n🔍 Testing Motivational Quote Endpoint")
    
    # Test with high priority
    try:
        quote_data = {
            "task_title": "Complete important presentation",
            "priority": "high",
            "context": "This is for a major client meeting tomorrow"
        }
        response = requests.post(f"{BASE_URL}/motivational-quote", json=quote_data)
        passed = response.status_code == 200 and "quote" in response.json() and "task" in response.json()
        log_test("Motivational Quote - High Priority", passed, "Should return a motivational quote for high priority task", response)
    except Exception as e:
        log_test("Motivational Quote - High Priority", False, f"Exception: {str(e)}")
    
    # Test with medium priority
    try:
        quote_data = {
            "task_title": "Update project documentation",
            "priority": "medium"
        }
        response = requests.post(f"{BASE_URL}/motivational-quote", json=quote_data)
        passed = response.status_code == 200 and "quote" in response.json() and "task" in response.json()
        log_test("Motivational Quote - Medium Priority", passed, "Should return a motivational quote for medium priority task", response)
    except Exception as e:
        log_test("Motivational Quote - Medium Priority", False, f"Exception: {str(e)}")
    
    # Test with low priority
    try:
        quote_data = {
            "task_title": "Organize digital files",
            "priority": "low"
        }
        response = requests.post(f"{BASE_URL}/motivational-quote", json=quote_data)
        passed = response.status_code == 200 and "quote" in response.json() and "task" in response.json()
        log_test("Motivational Quote - Low Priority", passed, "Should return a motivational quote for low priority task", response)
    except Exception as e:
        log_test("Motivational Quote - Low Priority", False, f"Exception: {str(e)}")

def run_all_tests():
    """Run all tests"""
    print("\n🚀 Starting Backend API Tests for Procrastinator App")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)
    
    # Basic endpoints
    test_health_check()
    test_stats_endpoint()
    
    # Project and task CRUD operations
    project_id = test_project_crud()
    task_id = test_task_crud(project_id)
    
    # Test task deletion
    if task_id:
        test_task_deletion(task_id)
    
    # Test project deletion with cascade
    new_project_id = test_project_crud()
    if new_project_id:
        test_project_deletion_cascade(new_project_id)
    
    # Test motivational quote
    test_motivational_quote()
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 80)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Success Rate: {(test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100):.2f}%")
    print("=" * 80)
    
    # Print failed tests for quick reference
    if test_results['failed'] > 0:
        print("\n❌ Failed Tests:")
        for test in test_results['tests']:
            if not test['passed']:
                print(f"- {test['name']}: {test['message']}")
        print("=" * 80)

if __name__ == "__main__":
    run_all_tests()