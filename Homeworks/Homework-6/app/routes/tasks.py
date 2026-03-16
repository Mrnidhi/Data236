from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime
from app.database import tasks_col
from app.models import TaskCreate, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

def serialize_task(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    task_dict = task.model_dump()
    task_dict["created_at"] = datetime.utcnow()
    task_dict["updated_at"] = datetime.utcnow()
    result = tasks_col.insert_one(task_dict)
    created = tasks_col.find_one({"_id": result.inserted_id})
    return serialize_task(created)

@router.get("")
def get_all_tasks():
    tasks = list(tasks_col.find({}))
    return [serialize_task(t) for t in tasks]

@router.get("/{task_id}")
def get_task(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    task = tasks_col.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return serialize_task(task)

@router.put("/{task_id}")
def update_task(task_id: str, task_update: TaskUpdate):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    update_data["updated_at"] = datetime.utcnow()
    result = tasks_col.update_one({"_id": ObjectId(task_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    task = tasks_col.find_one({"_id": ObjectId(task_id)})
    return serialize_task(task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    result = tasks_col.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
