import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILE = os.path.join(BASE_DIR, "users.json")

def load_users():
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def find_user(username):
    users = load_users()
    for user in users:
        if user["username"] == username:
            return user
    return None

def add_user(username, password, role):
    users = load_users()
    new_id = max([u["id"] for u in users], default=0) + 1
    users.append({"id": new_id, "username": username, "password": password, "role": role})
    save_users(users)
    return new_id