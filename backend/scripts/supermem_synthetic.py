import os
from pymongo import MongoClient
from supermemory import Supermemory
from bson import ObjectId
import json
from dotenv import load_dotenv
load_dotenv()

# --- MongoDB Setup ---
username = "gvsharshith_db_user"
password = "4SnPc6Zp2dOyWToP"
uri = f"mongodb+srv://{username}:{password}@development.edtqqxr.mongodb.net/?retryWrites=true&w=majority&appName=Development"
client = MongoClient(uri)
db = client["BackendSymtheticData"]

# --- Supermemory Setup ---
sm = Supermemory(api_key=os.getenv("SUPERMEMORY_API_KEY"))

def safe_json(doc):
    """Converts ObjectId, datetime, and other Mongo types to JSON-safe format."""
    return json.loads(json.dumps(doc, default=str))

# ------------ BLOCKERS COLLECTION ------------
def push_blockers():
    collection = db["blockers"]
    for doc in collection.find():
        metadata = safe_json(doc)
        content = f"[Blocker] {doc.get('title')} | Root Cause: {doc.get('root_cause')}"
        sm.memories.add({"content": content, "metadata": metadata})

# ------------ KEYWORDS COLLECTION ------------
def push_keywords():
    collection = db["keywords"]
    for doc in collection.find():
        for key, value in doc.items():
            if key == "_id": 
                continue
            content = f"[Keyword] {key}: {value}"
            sm.memories.add({
                "content": content,
                "metadata": {"keyword": key, "description": value}
            })

# ------------ PROJECTS COLLECTION ------------
def push_projects():
    collection = db["projects"]
    for doc in collection.find():
        metadata = safe_json(doc)
        content = f"[Project] {doc.get('name')} - {doc.get('description')}"
        sm.memories.add({"content": content, "metadata": metadata})

# ------------ TEAM MEMBERS COLLECTION ------------
def push_team_members():
    collection = db["teamMembers"]
    for doc in collection.find():
        metadata = safe_json(doc)
        content = f"[Team Member] {doc.get('name')} ({doc.get('role')}) - Current task: {doc.get('current_task')}"
        sm.memories.add({"content": content, "metadata": metadata})

# ------------ TICKETS COLLECTION ------------
def push_tickets():
    collection = db["tickets"]
    for doc in collection.find():
        metadata = safe_json(doc)
        content = f"[Ticket] {doc.get('id')} - {doc.get('title')} | Status: {doc.get('status')} | Assignee: {doc.get('assignee')}"
        sm.memories.add({"content": content, "metadata": metadata})

# ------------ RUN ALL ------------
if __name__ == "__main__":
    push_blockers()
    push_keywords()
    push_projects()
    push_team_members()
    push_tickets()
    print("✅ Finished pushing all MongoDB data to Supermemory!")
