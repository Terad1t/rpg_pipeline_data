import random
import json
import os
import pandas as pd
from pathlib import Path
from faker import Faker

fk = Faker("en_US")
current_dir = Path(__file__).parent
project_root = current_dir.parent
json_path = project_root / "data" / "dados.json" 

if json_path.exists():
    print(f"Lendo arquivo: {json_path}")
    df_users = pd.read_json(json_path)
    print(f"Arquivo carregado! {len(df_users)} usuários encontrados.")
else:
    print(f"ERRO: Arquivo não encontrado em {json_path}")
    print("Certifique-se de que o users.py foi executado e gerou o arquivo.")
    df_users = pd.DataFrame()

desktop = ["Discord Desktop", "Discord Web"]
devices = []

file = "data/"
path_file = os.path.join(file, "devices.json")
df_users = pd.read_json(json_path)

def generate_devices(num_characters):
    for _, user in df_users.iterrows():
        devices.append({
            "id" : user["id"],
            "username": user["name"], 
            "device_id": user ["device_id"],
            "created_at": fk.date_time_this_year().isoformat(),
            "player_client": random.choice(desktop)
        })
    return devices

with open(path_file, "w", encoding="utf-8") as f:
    json.dump(generate_devices(100), f, indent=4, ensure_ascii=False)




