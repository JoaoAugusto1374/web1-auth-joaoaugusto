from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import logging, os, jwt, datetime, base64
from helper import load_users, save_users, find_user, add_user
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Configurar logging
logging.basicConfig(level=app.config["LOG_LEVEL"])
logger = logging.getLogger(__name__)

# JWT
JWT_SECRET = "segredo_jwt"  
JWT_ALGO = "HS256"

# ---------------------- ROTAS ----------------------

@app.route("/")
def index():
    return render_template("index.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")
    ip = request.remote_addr

    logger.debug(f"Tentativa de login: user={username}, ip={ip}, senha=***")

    user = find_user(username)

    if not user or user["password"] != password:
        logger.debug(f"Login falhou: user={username}, motivo=credenciais inválidas")
        return "Credenciais inválidas", 401

    # --- Sessão ---
    session["user_id"] = user["id"]

    # --- JWT ---
    payload = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

    logger.debug(f"Login bem-sucedido: user={username}")
    logger.debug(f"JWT emitido: {payload}")

    return jsonify({"message": "Login OK", "token": token})

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    user = autenticar()
    if not user:
        return "Acesso negado", 401
    return render_template("dashboard.html", username=user["username"], role=user["role"])

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))

# ---------- GERENCIAMENTO DE USUÁRIOS ----------
@app.route("/users", methods=["GET", "POST"])
def users_route():
    user = autenticar()
    if not user:
        return "Não autorizado", 401
    if request.method == "GET":
        if user["role"] != "admin":
            return "Apenas admin pode ver", 403
        return jsonify(load_users())
    elif request.method == "POST":
        data = request.json
        novo = add_user(data["username"], data["password"], data.get("role", "user"))
        return jsonify(novo), 201

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = autenticar()
    if not user or user["role"] != "admin":
        return "Apenas admin pode deletar", 403
    users = load_users()
    users = [u for u in users if u["id"] != user_id]
    save_users(users)
    return jsonify({"message": "Usuário removido"})

# ---------------------- FUNÇÕES AUX DE AUTENTICAÇÃO ----------------------
def autenticar():
    # 1) Sessão
    if "user_id" in session:
        users = load_users()
        for u in users:
            if u["id"] == session["user_id"]:
                return u

    # 2) JWT
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            logger.debug(f"JWT válido: {payload}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.debug("JWT expirado")
        except jwt.InvalidTokenError:
            logger.debug("JWT inválido")

    # 3) Basic Auth
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Basic "):
        encoded = auth_header.split(" ")[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, password = decoded.split(":")
        user = find_user(username)
        if user and user["password"] == password:
            logger.debug(f"BasicAuth válido: user={username}")
            return user

    return None

# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
