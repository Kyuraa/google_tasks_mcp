from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
from datetime import datetime
from typing import List, Optional

# Google API imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

app = FastAPI()

# OAuth 2.0 scopes
SCOPES = ['https://www.googleapis.com/auth/tasks']

# Pydantic models
class TaskListCreate(BaseModel):
    title: str

class TaskListUpdate(BaseModel):
    title: str

class TaskLink(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None

class TaskCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Buy groceries"})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Don't forget eggs"})
    due: Optional[str] = Field(None, json_schema_extra={"example": "2025-11-10T09:00:00Z"})
    parent: Optional[str] = Field(None, description="Parent task ID for subtasks")
    previous: Optional[str] = Field(None, description="Previous sibling task ID")
    status: Optional[str] = Field("needsAction", json_schema_extra={"example": "needsAction"})

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    due: Optional[str] = None
    status: Optional[str] = None  # needsAction | completed
    completed: Optional[str] = None
    parent: Optional[str] = None
    previous: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    title: Optional[str] = None
    notes: Optional[str] = None
    due: Optional[str] = None
    status: Optional[str] = None
    completed: Optional[str] = None
    deleted: Optional[bool] = None
    hidden: Optional[bool] = None
    updated: Optional[str] = None
    parent: Optional[str] = None
    position: Optional[str] = None
    links: Optional[List[TaskLink]] = None
    selfLink: Optional[str] = None
    webViewLink: Optional[str] = None

# Google API service functions
def get_google_service():
    """Get authenticated Google Tasks service using tokens.json"""

    # Load tokens from tokens.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, 'tokens.json')

    if not os.path.exists(token_path):
        raise HTTPException(
            status_code=500,
            detail=f"tokens.json not found at {token_path}"
        )

    try:
        with open(token_path, 'r') as f:
            import json
            token_data = json.load(f)

        # Create credentials object (same as working test script)
        creds = Credentials(
            None,  # No access token initially
            refresh_token=token_data["refresh_token"],
            client_id=token_data["client_id"],
            client_secret=token_data["client_secret"],
            token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token")
        )

        # Build the service
        service = build('tasks', 'v1', credentials=creds)
        return service

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Google Tasks service: {str(e)}"
        )

# API Endpoints

@app.get("/")
def read_root():
    return {"message": "Welcome to the Google Tasks API Service!"}

@app.get("/tasklists")
def list_tasklists():
    """List all task lists"""
    service = get_google_service()
    try:
        results = service.tasklists().list().execute()
        return {"tasklists": results.get('items', [])}
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.post("/tasklists")
def create_tasklist(request: TaskListCreate):
    """Create a new task list"""
    service = get_google_service()
    try:
        result = service.tasklists().insert(body={"title": request.title}).execute()
        return result
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.get("/tasklists/{tasklist_id}")
def get_tasklist(tasklist_id: str):
    """Get a specific task list"""
    service = get_google_service()
    try:
        result = service.tasklists().get(tasklist=tasklist_id).execute()
        return result
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.put("/tasklists/{tasklist_id}")
def update_tasklist(tasklist_id: str, request: TaskListUpdate):
    """Update a task list"""
    service = get_google_service()
    try:
        result = service.tasklists().update(tasklist=tasklist_id, body={"title": request.title}).execute()
        return result
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.delete("/tasklists/{tasklist_id}")
def delete_tasklist(tasklist_id: str):
    """Delete a task list"""
    service = get_google_service()
    try:
        service.tasklists().delete(tasklist=tasklist_id).execute()
        return {"message": "Task list deleted successfully"}
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.get("/tasklists/{tasklist_id}/tasks")
def list_tasks(tasklist_id: str):
    """List tasks in a task list"""
    service = get_google_service()
    try:
        results = service.tasks().list(tasklist=tasklist_id).execute()
        return {"tasks": results.get('items', [])}
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.post("/tasklists/{tasklist_id}/tasks")
def create_task(tasklist_id: str, request: TaskCreate):
    """Create a new task"""
    service = get_google_service()
    try:
        body = {"title": request.title}
        if request.notes is not None:
            body["notes"] = request.notes
        if request.due is not None:
            body["due"] = request.due
        if request.parent is not None:
            body["parent"] = request.parent
        if request.previous is not None:
            body["previous"] = request.previous
        if request.status is not None:
            body["status"] = request.status

        result = service.tasks().insert(tasklist=tasklist_id, body=body).execute()
        return result
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.get("/tasklists/{tasklist_id}/tasks/{task_id}")
def get_task(tasklist_id: str, task_id: str):
    """Get a specific task"""
    service = get_google_service()
    try:
        result = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        return result
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.put("/tasklists/{tasklist_id}/tasks/{task_id}")
def update_task(tasklist_id: str, task_id: str, request: TaskUpdate):
    """Update a task"""
    service = get_google_service()
    try:
        body = {}
        if request.title is not None:
            body["title"] = request.title
        if request.notes is not None:
            body["notes"] = request.notes
        if request.due is not None:
            body["due"] = request.due
        if request.status is not None:
            body["status"] = request.status
        if request.completed is not None:
            body["completed"] = request.completed
        if request.parent is not None:
            body["parent"] = request.parent
        if request.previous is not None:
            body["previous"] = request.previous

        result = service.tasks().update(tasklist=tasklist_id, task=task_id, body=body).execute()
        return result
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.delete("/tasklists/{tasklist_id}/tasks/{task_id}")
def delete_task(tasklist_id: str, task_id: str):
    """Delete a task"""
    service = get_google_service()
    try:
        service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
        return {"message": "Task deleted successfully"}
    except HttpError as err:
        raise HTTPException(status_code=err.resp.status, detail=str(err))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
