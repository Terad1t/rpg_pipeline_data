import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

ENV_PATH = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(ENV_PATH)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "http://host.docker.internal:5000"

def extract_data(endpoint: str) -> list:
    api_key = os.getenv("API_KEY")

    if not api_key:
        logging.error("API_KEY não encontrada no .env — a API foi iniciada?")
        return []

    headers = {"X-API-Key": api_key}
    response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers)

    if response.status_code == 401:
        logging.error(f"API Key inválida para /{endpoint}")
        return []

    if response.status_code != 200:
        logging.error(f"Erro ao buscar /{endpoint}: {response.status_code}")
        return []

    data = response.json()
    logging.info(f"/{endpoint}: {len(data)} registro(s) extraído(s)")
    return data

def extract_all():
    return {
        "users":      extract_data("users"),
        "characters": extract_data("characters"),
        "devices":    extract_data("devices"),
    }