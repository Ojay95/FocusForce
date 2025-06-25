#!/usr/bin/env python3
import json
import time
import uuid
import subprocess
from datetime import datetime, timedelta

# Base URL for testing
BASE_URL = "http://localhost:8001/api"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def run_curl(method, endpoint, data=None):
    """Run a curl command and return the response"""
    url = f"{BASE_URL}/{endpoint}"
    
    if method.upper() == "GET":
        cmd = ["curl", "-s", url]
    elif method.upper() == "POST":
        cmd = ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(data), url]
    elif method.upper() == "PUT":
        cmd = ["curl", "-s", "-X", "PUT", "-H", "Content-Type: application/json", "-d", json.dumps(data), url]
    elif method.upper() == "DELETE":
        cmd = ["curl", "-s", "-X", "DELETE", url]
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {"success": False, "status_code": result.returncode, "data": result.stderr}
        
        try:
            if "Internal Server Error" in result.stdout:
                return {"success": False, "status_code": 500, "data": "Internal Server Error"}
            
            response_data = json.loads(result.stdout)
            return {"success": True, "status_code": 200, "data": response_data}
        except json.JSONDecodeError:
            return {"success": False, "status_code": 500, "data": result.stdout}
    except Exception as e:
        return {"success": False, "status_code": 500, "data": str(e)}

def log_test(name, passed, message="", response=None):
    """Log test results"""
    status = "✅ PASSED" if passed else "❌ FAILED"
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "message": message,
        "response": response
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    print(f"{status} - {name}")
    if message:
        print(f"  {message}")
    if response:
        print(f"  Status: {response.get('status_code')}")
        print(f"  Response: {json.dumps(response.get('data'), indent=2)}")
    print("-" * 80)

def test_health_check():
    """Test the health check endpoint"""
    print("\n🔍 Testing Health Check Endpoint")
    try:
        response = run_curl("GET", "health")
        passed = response["success"] and "status" in response["data"] and response["data"]["status"] == "healthy"
        log_test("Health Check Endpoint", passed, "Health check endpoint should return status 'healthy'", response)
    except Exception as e:
        log_test("Health Check Endpoint", False, f"Exception: {str(e)}")

def test_stats_endpoint():
    """Test the stats endpoint"""
    print("\n🔍 Testing Stats Endpoint")
    try:
        response = run_curl("GET", "stats")
        passed = response["success"] and "total_tasks" in response["data"]
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
        response = run_curl("POST", "projects", project_data)
        project_id = response["data"].get("id")
        passed = response["success"] and "id" in response["data"] and response["data"]["name"] == project_data["name"]
        log_test("Create Project", passed, "Should create a new project", response)
    except Exception as e:
        log_test("Create Project", False, f"Exception: {str(e)}")
        return
    
    # Get all projects
    try:
        response = run_curl("GET", "projects")
        passed = response["success"] and isinstance(response["data"], list)
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
            response = run_curl("PUT", f"projects/{project_id}", updated_data)
            passed = response["success"] and response["data"]["name"] == updated_data["name"]
            log_test("Update Project", passed, "Should update an existing project", response)
        except Exception as e:
            log_test("Update Project", False, f"Exception: {str(e)}")
    
    # Test invalid project update
    try:
        invalid_id = str(uuid.uuid4())
        response = run_curl("PUT", f"projects/{invalid_id}", {"name": "Invalid Project"})
        passed = not response["success"] or response.get("status_code") == 404
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
        response = run_curl("POST", "tasks", task_data)
        task_id = response["data"].get("id")
        passed = response["success"] and "id" in response["data"] and response["data"]["title"] == task_data["title"]
        log_test("Create Task", passed, "Should create a new task", response)
    except Exception as e:
        log_test("Create Task", False, f"Exception: {str(e)}")
        return
    
    # Get all tasks
    try:
        response = run_curl("GET", "tasks")
        passed = response["success"] and isinstance(response["data"], list)
        log_test("Get All Tasks", passed, "Should return a list of tasks", response)
    except Exception as e:
        log_test("Get All Tasks", False, f"Exception: {str(e)}")
    
    # Get tasks by project
    if project_id:
        try:
            response = run_curl("GET", f"tasks?project_id={project_id}")
            passed = response["success"] and isinstance(response["data"], list)
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
            response = run_curl("PUT", f"tasks/{task_id}", updated_data)
            passed = response["success"] and response["data"]["title"] == updated_data["title"]
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
            response = run_curl("PUT", f"tasks/{task_id}", completed_data)
            passed = (response["success"] and 
                     response["data"]["status"] == "completed" and 
                     "completed_at" in response["data"] and 
                     response["data"]["completed_at"] is not None)
            log_test("Complete Task", passed, "Should mark task as completed and set completed_at", response)
        except Exception as e:
            log_test("Complete Task", False, f"Exception: {str(e)}")
    
    # Test invalid task update
    try:
        invalid_id = str(uuid.uuid4())
        response = run_curl("PUT", f"tasks/{invalid_id}", {"title": "Invalid Task"})
        passed = not response["success"] or response.get("status_code") == 404
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
        response = run_curl("DELETE", f"tasks/{task_id}")
        passed = response["success"] and "message" in response["data"]
        log_test("Delete Task", passed, "Should delete an existing task", response)
        
        # Verify task is deleted
        response = run_curl("GET", "tasks")
        task_exists = any(task.get("id") == task_id for task in response["data"])
        passed = not task_exists
        log_test("Verify Task Deletion", passed, "Deleted task should not appear in task list")
    except Exception as e:
        log_test("Delete Task", False, f"Exception: {str(e)}")
    
    # Test invalid task deletion
    try:
        invalid_id = str(uuid.uuid4())
        response = run_curl("DELETE", f"tasks/{invalid_id}")
        passed = not response["success"] or response.get("status_code") == 404
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
            response = run_curl("POST", "tasks", task_data)
            if response["success"]:
                task_ids.append(response["data"].get("id"))
        except Exception:
            pass
    
    # Verify tasks were created
    try:
        response = run_curl("GET", f"tasks?project_id={project_id}")
        passed = response["success"] and len(response["data"]) >= len(task_ids)
        log_test("Create Tasks for Cascade Test", passed, f"Created {len(task_ids)} tasks for project", response)
    except Exception as e:
        log_test("Create Tasks for Cascade Test", False, f"Exception: {str(e)}")
        return
    
    # Delete the project
    try:
        response = run_curl("DELETE", f"projects/{project_id}")
        passed = response["success"] and "message" in response["data"]
        log_test("Delete Project", passed, "Should delete an existing project", response)
    except Exception as e:
        log_test("Delete Project", False, f"Exception: {str(e)}")
        return
    
    # Verify project is deleted
    try:
        response = run_curl("GET", "projects")
        project_exists = any(project.get("id") == project_id for project in response["data"])
        passed = not project_exists
        log_test("Verify Project Deletion", passed, "Deleted project should not appear in project list")
    except Exception as e:
        log_test("Verify Project Deletion", False, f"Exception: {str(e)}")
    
    # Verify associated tasks are deleted
    try:
        response = run_curl("GET", "tasks")
        tasks_exist = any(task.get("project_id") == project_id for task in response["data"])
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
        response = run_curl("POST", "motivational-quote", quote_data)
        passed = response["success"] and "quote" in response["data"] and "task" in response["data"]
        log_test("Motivational Quote - High Priority", passed, "Should return a motivational quote for high priority task", response)
    except Exception as e:
        log_test("Motivational Quote - High Priority", False, f"Exception: {str(e)}")
    
    # Test with medium priority
    try:
        quote_data = {
            "task_title": "Update project documentation",
            "priority": "medium"
        }
        response = run_curl("POST", "motivational-quote", quote_data)
        passed = response["success"] and "quote" in response["data"] and "task" in response["data"]
        log_test("Motivational Quote - Medium Priority", passed, "Should return a motivational quote for medium priority task", response)
    except Exception as e:
        log_test("Motivational Quote - Medium Priority", False, f"Exception: {str(e)}")
    
    # Test with low priority
    try:
        quote_data = {
            "task_title": "Organize digital files",
            "priority": "low"
        }
        response = run_curl("POST", "motivational-quote", quote_data)
        passed = response["success"] and "quote" in response["data"] and "task" in response["data"]
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