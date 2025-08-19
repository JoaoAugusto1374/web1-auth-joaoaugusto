import os
import logging
import datetime
import jwt
from flask import Flask, request, jsonify, render_template, make_response
from helper import load_users, save_users, find_user, add_user
from config import SECRET_KEY, LOG_LEVEL, JWT_EXPIRATION

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

logging.basicConfig(level=LOG_LEVEL)

# Criar JWT
def create_jwt(user):
    payload = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=JWT_EXPIRATION)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    logging.debug(f"JWT payload: {payload}")
    return token

# Decorator JWT
def jwt_required(admin_only=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
            elif "jwt" in request.cookies:
                token = request.cookies.get("jwt")
            if not token:
                return jsonify({"error": "Token ausente"}), 401
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Token inválido"}), 401
            if admin_only and payload.get("role") != "admin":
                return jsonify({"error": "Permissão negada"}), 403
            return func(payload, *args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

# --- Rotas ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json() if request.is_json else request.form
    username = data.get("username")
    password = data.get("password")

    user = find_user(username)
    if not user or user["password"] != password:
        logging.debug(f"Falha login: {username}, senha mascarada: {'*'*len(password)}")
        return jsonify({"error": "Usuário ou senha inválidos"}), 401

    token = create_jwt(user)
    logging.debug(f"Login sucesso: {username}")

    if user["role"] == "admin":
        # Admin → envia cookie HttpOnly e redireciona
        response = make_response(render_template("dashboard.html", username=user["username"], role=user["role"], users=load_users()))
        response.set_cookie("jwt", token, httponly=True)
        return response
    else:
        # Usuário comum → apenas JSON
        return jsonify({"message": "Login bem-sucedido", "token": token, "role": user["role"]})

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout realizado"})
    response.set_cookie("jwt", "", expires=0)
    return response

@app.route("/dashboard", methods=["GET", "POST", "DELETE"])
@jwt_required(admin_only=True)
def dashboard(payload):
    users = load_users()

    if request.method == "GET":
        return render_template("dashboard.html", username=payload["username"], role=payload["role"], users=users)

    if request.method == "POST":
        data = request.get_json()
        username_new = data.get("username")
        password_new = data.get("password")
        role_new = data.get("role")
        if not username_new or not password_new or not role_new:
            return jsonify({"error": "Campos faltando"}), 400
        user_id = add_user(username_new, password_new, role_new)
        return jsonify({"message": "Usuário criado", "id": user_id})

    if request.method == "DELETE":
        data = request.get_json()
        user_id = data.get("id")
        if not user_id:
            return jsonify({"error": "ID do usuário faltando"}), 400
        user_id = int(user_id)
        user = next((u for u in users if u["id"] == user_id), None)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        users.remove(user)
        save_users(users)
        return jsonify({"message": "Usuário removido"})

if __name__ == "__main__":
    app.run(debug=True)
