from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pymongo
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import uuid
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/procrastinator_app')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

client = pymongo.MongoClient(MONGO_URL)
db = client.procrastinator_app

# Collections
tasks_collection = db.tasks
projects_collection = db.projects

# Pydantic models
class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = ""
    priority: str = "medium"  # low, medium, high
    status: str = "todo"  # todo, in_progress, completed
    due_date: Optional[str] = None
    project_id: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

class Project(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = ""
    color: str = "#a855f7"
    created_at: Optional[str] = None

class MotivationalQuoteRequest(BaseModel):
    task_title: str
    priority: str
    context: Optional[str] = ""

# Initialize Gemini AI chat
def get_motivational_chat():
    return LlmChat(
        api_key=GEMINI_API_KEY,
        session_id=f"motivation_{uuid.uuid4()}",
        system_message="You are an inspiring motivational coach who generates powerful, personalized quotes to help users overcome procrastination and stay focused on their tasks. Generate contextual quotes based on the user's current task, priority level, and situation. Keep quotes under 100 words, make them actionable and inspiring."
    ).with_model("gemini", "gemini-2.0-flash")

@app.get("/")
async def root():
    return {"message": "Procrastinator App API"}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# AI Motivational Quotes
@app.post("/api/motivational-quote")
async def get_motivational_quote(request: MotivationalQuoteRequest):
    try:
        chat = get_motivational_chat()
        
        priority_context = {
            "high": "urgent and important",
            "medium": "moderately important",
            "low": "worth completing when you have time"
        }
        
        prompt = f"Generate a motivational quote for someone who needs to work on: '{request.task_title}'. This task is {priority_context.get(request.priority, 'important')}. {request.context if request.context else ''} Make it inspiring and actionable to beat procrastination."
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return {"quote": response, "task": request.task_title}
    except Exception as e:
        return {"quote": "You've got this! Every small step counts towards your goal. Start now, start today!", "task": request.task_title}

# Task endpoints
@app.get("/api/tasks", response_model=List[Task])
async def get_tasks(project_id: Optional[str] = None):
    try:
        filter_query = {}
        if project_id:
            filter_query["project_id"] = project_id
        
        tasks = list(tasks_collection.find(filter_query))
        for task in tasks:
            task["id"] = task.pop("_id")
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks", response_model=Task)
async def create_task(task: Task):
    try:
        task_dict = task.dict()
        task_dict["id"] = str(uuid.uuid4())
        task_dict["created_at"] = datetime.now().isoformat()
        task_dict.pop("_id", None)
        
        tasks_collection.insert_one(task_dict)
        return task_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task: Task):
    try:
        task_dict = task.dict()
        task_dict["id"] = task_id
        
        if task.status == "completed" and task_dict.get("completed_at") is None:
            task_dict["completed_at"] = datetime.now().isoformat()
        
        result = tasks_collection.replace_one({"id": task_id}, task_dict)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    try:
        result = tasks_collection.delete_one({"id": task_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Project endpoints
@app.get("/api/projects", response_model=List[Project])
async def get_projects():
    try:
        projects = list(projects_collection.find())
        for project in projects:
            project["id"] = str(project.pop("_id"))
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects", response_model=Project)
async def create_project(project: Project):
    try:
        project_dict = project.dict()
        project_dict["id"] = str(uuid.uuid4())
        project_dict["created_at"] = datetime.now().isoformat()
        project_dict.pop("_id", None)
        
        projects_collection.insert_one(project_dict)
        return project_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project: Project):
    try:
        project_dict = project.dict()
        project_dict["id"] = project_id
        
        result = projects_collection.replace_one({"id": project_id}, project_dict)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return project_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    try:
        # Delete all tasks associated with this project
        tasks_collection.delete_many({"project_id": project_id})
        
        # Delete the project
        result = projects_collection.delete_one({"id": project_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {"message": "Project and associated tasks deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stats endpoint
@app.get("/api/stats")
async def get_stats():
    try:
        total_tasks = tasks_collection.count_documents({})
        completed_tasks = tasks_collection.count_documents({"status": "completed"})
        in_progress_tasks = tasks_collection.count_documents({"status": "in_progress"})
        total_projects = projects_collection.count_documents({})
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "total_projects": total_projects,
            "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)