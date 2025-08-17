import json
import os

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def find_user(username):
    users = load_users()
    for u in users:
        if u["username"] == username:
            return u
    return None

def add_user(username, password, role="user"):
    users = load_users()
    new_id = max([u["id"] for u in users]) + 1 if users else 1
    new_user = {"id": new_id, "username": username, "password": password, "role": role}
    users.append(new_user)
    save_users(users)
    return new_user
