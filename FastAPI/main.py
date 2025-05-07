from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Todo(BaseModel):
    id: int
    item: str
    completed: bool = False

# In-memory storage
todos: List[Todo] = []

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "Welcome to my Todo Application"}

@app.get("/todos", status_code=status.HTTP_200_OK)
async def get_todos():
    return {"todos": todos}

@app.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return {"todo": todo}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo):
    # Check for existing ID to prevent duplicates
    for existing_todo in todos:
        if existing_todo.id == todo.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Todo with this ID already exists")
    
    todos.append(todo)
    return {"message": "Todo has been added", "todo": todo}

@app.put("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(todo_id: int, todo_obj: Todo):
    for todo in todos:
        if todo.id == todo_id:
            todo.item = todo_obj.item
            todo.completed = todo_obj.completed
            return {"message": "Todo updated", "todo": todo}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')

@app.patch("/todos/{todo_id}/complete", status_code=status.HTTP_200_OK)
async def toggle_complete(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            todo.completed = not todo.completed
            return {"message": "Todo completion status toggled", "todo": todo}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            todos.remove(todo)
            return {"message": "Todo removed"}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')
