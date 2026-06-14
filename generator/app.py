from flask import Flask, request, jsonify
from functools import wraps
import os, secrets
from dotenv import load_dotenv, set_key
from pathlib import Path

from users import generate_users
from characters import generate_characters
from devices import generate_devices

ENV_PATH = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(ENV_PATH)

app = Flask(__name__)

# ── Gera API Key ──
def generate_api_key():
    existing_key = os.getenv("API_KEY")
    if existing_key:
        print("[API] API_KEY já existe, reutilizando.")
        return existing_key
    
    ENV_PATH.parent.mkdir(parents=True, exist_ok=True)  # ← essa linha está aqui?
    new_key = secrets.token_hex(32)
    set_key(ENV_PATH, "API_KEY", new_key)
    os.environ["API_KEY"] = new_key
    print(f"[API] Nova API_KEY gerada e salva em {ENV_PATH}")
    return new_key

# ── Gera dados no startup ──
def generate_all_data():
    print("[API] Gerando dados simulados...")
    users      = generate_users(5)
    characters = generate_characters(users)   # depende de users
    devices    = generate_devices(users)      # depende de users
    print(f"[API] {len(users)} users, {len(characters)} characters, {len(devices)} devices gerados.")
    return users, characters, devices

API_KEY                                  = generate_api_key()
users_data, characters_data, devices_data = generate_all_data()

# ── Decorator ──
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ── GET routes ──
@app.route("/users", methods=["GET"])
@require_api_key
def send_users():
    return jsonify(users_data), 200

@app.route("/characters", methods=["GET"])
@require_api_key
def send_characters():
    return jsonify(characters_data), 200

@app.route("/devices", methods=["GET"])
@require_api_key
def send_devices():
    return jsonify(devices_data), 200

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, port=5000)