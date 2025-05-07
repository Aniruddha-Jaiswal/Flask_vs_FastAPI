from flask import Flask, request, jsonify
from dataclasses import dataclass, field
from typing import List

app = Flask(__name__)

@dataclass
class Todo:
    id: int
    item: str
    completed: bool = False

# In-memory storage
todos: List[Todo] = []

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Welcome to my Todo Application"})

@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify({"todos": [todo.__dict__ for todo in todos]})

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    for todo in todos:
        if todo.id == todo_id:
            return jsonify({"todo": todo.__dict__})
    return jsonify({"error": "Todo not found"}), 404

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    
    # Check for existing ID to prevent duplicates
    for existing_todo in todos:
        if existing_todo.id == data.get('id'):
            return jsonify({"error": "Todo with this ID already exists"}), 400
    
    new_todo = Todo(
        id=data.get('id'),
        item=data.get('item'),
        completed=data.get('completed', False)
    )
    todos.append(new_todo)
    return jsonify({"message": "Todo has been added", "todo": new_todo.__dict__}), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    for todo in todos:
        if todo.id == todo_id:
            todo.item = data.get('item', todo.item)
            todo.completed = data.get('completed', todo.completed)
            return jsonify({"message": "Todo updated", "todo": todo.__dict__})
    return jsonify({"error": "Todo not found"}), 404

@app.route('/todos/<int:todo_id>/complete', methods=['PATCH'])
def toggle_complete(todo_id):
    for todo in todos:
        if todo.id == todo_id:
            todo.completed = not todo.completed
            return jsonify({"message": "Todo completion status toggled", "todo": todo.__dict__})
    return jsonify({"error": "Todo not found"}), 404

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    for todo in todos:
        if todo.id == todo_id:
            todos.remove(todo)
            return jsonify({"message": "Todo removed"}), 204
    return jsonify({"error": "Todo not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)