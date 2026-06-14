import random
import json
import os
import pandas as pd
from pathlib import Path
from faker import Faker

fk = Faker("en_US")
current_dir = Path(__file__).parent
project_root = current_dir.parent
json_path = project_root / "data" / "dados.json"  # Mudar de users.json para dados.json

# Verificar se o arquivo existe
if json_path.exists():
    print(f"Lendo arquivo: {json_path}")
    df_users = pd.read_json(json_path)
    print(f"Arquivo carregado! {len(df_users)} usuários encontrados.")
else:
    print(f"ERRO: Arquivo não encontrado em {json_path}")
    print("Certifique-se de que o users.py foi executado e gerou o arquivo.")
    df_users = pd.DataFrame()  # DataFrame vazio como fallback

# These lists are used to generate random usernames by combining elements from each list.
Init = ["Vol'", "Mal", "Sor'", "Zel'", "Tar'", "Val'", "Kor'", "Nar'", "Zel'", "Mar'"
        "Zode", "Vex'", "Xar", "Yol", "Zor'", "Kro'", "Nex ", "Zel", "Mar'", "Milon"]
Mei = ["ael", "zonite", "aeroid", "one", "ieol", "funel",
       "zineta", " Zygon", " Bygon", "kyath", "iul"]
Fim = [" Tontatta", " Chusinsaa", " Lan'gon", " Daz", " Kuro", " Xi'Zoe"]

file = "data/"
path_file = os.path.join(file, "characters.json")
df_users = pd.read_json(json_path)


characters = []

def generate_characters(num_characters):
    for _, user_id in df_users.iterrows():
        characters.append({
            "character_name": random.choice(Init) + random.choice(Mei) + random.choice(Fim),
            "id" : user_id["id"],
            "username": user_id["name"], 
            "character_id": fk.uuid4(),
            "created_at": fk.date_time_this_year().isoformat()
        })

    return characters

with open(path_file, "w", encoding="utf-8") as f:
    json.dump(generate_characters(100), f, indent=4, ensure_ascii=False)