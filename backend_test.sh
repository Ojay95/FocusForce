#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8001/api"

# Test counter
PASSED=0
FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_status="$3"
    local validation_command="$4"
    
    echo -e "\n${BLUE}Testing: ${test_name}${NC}"
    echo "Command: $command"
    
    # Run the command and capture output
    response=$(eval "$command")
    exit_code=$?
    
    # Check if the command succeeded
    if [ $exit_code -eq 0 ]; then
        echo -e "Response: $response"
        
        # Run validation if provided
        if [ ! -z "$validation_command" ]; then
            if eval "$validation_command \"$response\""; then
                echo -e "${GREEN}✅ PASSED: $test_name${NC}"
                PASSED=$((PASSED + 1))
            else
                echo -e "${RED}❌ FAILED: $test_name (Validation failed)${NC}"
                FAILED=$((FAILED + 1))
            fi
        else
            echo -e "${GREEN}✅ PASSED: $test_name${NC}"
            PASSED=$((PASSED + 1))
        fi
    else
        echo -e "${RED}❌ FAILED: $test_name (Exit code: $exit_code)${NC}"
        FAILED=$((FAILED + 1))
    fi
    
    echo "----------------------------------------"
}

echo -e "${BLUE}🚀 Starting Backend API Tests for Procrastinator App${NC}"
echo -e "Base URL: $BASE_URL"
echo "==============================================="

# Test Health Check Endpoint
run_test "Health Check Endpoint" \
    "curl -s $BASE_URL/health" \
    200 \
    "grep -q 'healthy' <<< \$1"

# Test Stats Endpoint
run_test "Stats Endpoint" \
    "curl -s $BASE_URL/stats" \
    200 \
    "grep -q 'total_tasks' <<< \$1"

# Create a project
PROJECT_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{
        "name": "Test Project",
        "description": "A test project for API testing",
        "color": "#ff5733"
    }' \
    $BASE_URL/projects)

PROJECT_ID=$(echo $PROJECT_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ FAILED: Create Project (Could not extract project ID)${NC}"
    echo "Response: $PROJECT_RESPONSE"
    FAILED=$((FAILED + 1))
else
    echo -e "${GREEN}✅ PASSED: Create Project (ID: $PROJECT_ID)${NC}"
    PASSED=$((PASSED + 1))
    
    # Test Get Projects
    run_test "Get Projects" \
        "curl -s $BASE_URL/projects" \
        200 \
        "grep -q '$PROJECT_ID' <<< \$1"
    
    # Test Update Project
    run_test "Update Project" \
        "curl -s -X PUT -H \"Content-Type: application/json\" -d '{\"name\":\"Updated Project\",\"description\":\"An updated test project\",\"color\":\"#33ff57\"}' $BASE_URL/projects/$PROJECT_ID" \
        200 \
        "grep -q 'Updated Project' <<< \$1"
    
    # Create a task
    TASK_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
        -d '{
            "title": "Test Task",
            "description": "A test task for API testing",
            "priority": "high",
            "status": "todo",
            "project_id": "'$PROJECT_ID'"
        }' \
        $BASE_URL/tasks)
    
    TASK_ID=$(echo $TASK_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$TASK_ID" ]; then
        echo -e "${RED}❌ FAILED: Create Task (Could not extract task ID)${NC}"
        echo "Response: $TASK_RESPONSE"
        FAILED=$((FAILED + 1))
    else
        echo -e "${GREEN}✅ PASSED: Create Task (ID: $TASK_ID)${NC}"
        PASSED=$((PASSED + 1))
        
        # Test Get Tasks
        run_test "Get Tasks" \
            "curl -s $BASE_URL/tasks" \
            200 \
            "grep -q '$TASK_ID' <<< \$1"
        
        # Test Get Tasks by Project
        run_test "Get Tasks by Project" \
            "curl -s \"$BASE_URL/tasks?project_id=$PROJECT_ID\"" \
            200 \
            "grep -q '$TASK_ID' <<< \$1"
        
        # Test Update Task
        run_test "Update Task" \
            "curl -s -X PUT -H \"Content-Type: application/json\" -d '{\"title\":\"Updated Task\",\"description\":\"An updated test task\",\"priority\":\"medium\",\"status\":\"in_progress\"}' $BASE_URL/tasks/$TASK_ID" \
            200 \
            "grep -q 'Updated Task' <<< \$1"
        
        # Test Complete Task
        run_test "Complete Task" \
            "curl -s -X PUT -H \"Content-Type: application/json\" -d '{\"title\":\"Completed Task\",\"description\":\"A completed test task\",\"priority\":\"low\",\"status\":\"completed\"}' $BASE_URL/tasks/$TASK_ID" \
            200 \
            "grep -q 'completed_at' <<< \$1"
        
        # Test Delete Task
        run_test "Delete Task" \
            "curl -s -X DELETE $BASE_URL/tasks/$TASK_ID" \
            200 \
            "grep -q 'deleted successfully' <<< \$1"
        
        # Verify Task Deletion
        run_test "Verify Task Deletion" \
            "curl -s $BASE_URL/tasks" \
            200 \
            "! grep -q '$TASK_ID' <<< \$1"
    fi
    
    # Create tasks for cascade deletion test
    for i in {1..2}; do
        TASK_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
            -d '{
                "title": "Cascade Test Task '$i'",
                "description": "A test task for cascade deletion testing",
                "priority": "medium",
                "project_id": "'$PROJECT_ID'"
            }' \
            $BASE_URL/tasks)
        
        TASK_ID=$(echo $TASK_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
        
        if [ ! -z "$TASK_ID" ]; then
            echo -e "${GREEN}✅ PASSED: Create Task for Cascade Test (ID: $TASK_ID)${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}❌ FAILED: Create Task for Cascade Test${NC}"
            FAILED=$((FAILED + 1))
        fi
    done
    
    # Test Delete Project with Cascade
    run_test "Delete Project with Cascade" \
        "curl -s -X DELETE $BASE_URL/projects/$PROJECT_ID" \
        200 \
        "echo \$1 | grep -q 'deleted successfully'"
    
    # Verify Project Deletion
    run_test "Verify Project Deletion" \
        "curl -s $BASE_URL/projects" \
        200 \
        "! echo \$1 | grep -q '$PROJECT_ID'"
    
    # Verify Cascade Deletion
    run_test "Verify Cascade Deletion" \
        "curl -s \"$BASE_URL/tasks?project_id=$PROJECT_ID\"" \
        200 \
        "echo \$1 | grep -q '\[\]'"
fi

# Test Motivational Quote
run_test "Motivational Quote - High Priority" \
    "curl -s -X POST -H \"Content-Type: application/json\" -d '{\"task_title\":\"Complete important presentation\",\"priority\":\"high\",\"context\":\"This is for a major client meeting tomorrow\"}' $BASE_URL/motivational-quote" \
    200 \
    "echo \$1 | grep -q 'quote'"

run_test "Motivational Quote - Medium Priority" \
    "curl -s -X POST -H \"Content-Type: application/json\" -d '{\"task_title\":\"Update project documentation\",\"priority\":\"medium\"}' $BASE_URL/motivational-quote" \
    200 \
    "echo \$1 | grep -q 'quote'"

run_test "Motivational Quote - Low Priority" \
    "curl -s -X POST -H \"Content-Type: application/json\" -d '{\"task_title\":\"Organize digital files\",\"priority\":\"low\"}' $BASE_URL/motivational-quote" \
    200 \
    "echo \$1 | grep -q 'quote'"

# Test Invalid Requests
run_test "Invalid Task Update" \
    "curl -s -X PUT -H \"Content-Type: application/json\" -d '{\"title\":\"Invalid Task\"}' $BASE_URL/tasks/invalid-id" \
    404 \
    "echo \$1 | grep -q 'Task not found'"

run_test "Invalid Project Update" \
    "curl -s -X PUT -H \"Content-Type: application/json\" -d '{\"name\":\"Invalid Project\"}' $BASE_URL/projects/invalid-id" \
    404 \
    "echo \$1 | grep -q 'Project not found'"

# Print summary
echo -e "\n${BLUE}📊 Test Summary${NC}"
echo "==============================================="
TOTAL=$((PASSED + FAILED))
SUCCESS_RATE=$(awk "BEGIN {printf \"%.2f\", ($PASSED / $TOTAL) * 100}")
echo -e "Total Tests: $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo -e "Success Rate: $SUCCESS_RATE%"
echo "==============================================="