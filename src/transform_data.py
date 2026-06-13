import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_dataframe_from_api(users: list, characters: list, devices: list) -> pd.DataFrame:
    logging.info("Criando DataFrames...")

    df_users      = pd.json_normalize(users)
    df_characters = pd.json_normalize(characters)
    df_devices    = pd.json_normalize(devices)

    # Renomeia created_at antes do merge para evitar colisão
    df_characters = df_characters.rename(columns={
        "created_at": "character_created_at",
        "username": "character_username",    # redundante com name de users
        "character_name": "character_name",
        "character_id": "character_id",
    })

    df_devices = df_devices.rename(columns={
        "created_at": "device_created_at",
        "username": "device_username",       # redundante com name de users
        "device_id": "device_id",
        "player_client": "player_client",
    })

    logging.info("Fazendo merge dos DataFrames pela chave 'id'...")
    df = df_users.merge(df_characters, on="id")
    df = df.merge(df_devices, on="id")

    logging.info(f"DataFrame final: {len(df)} linha(s), {len(df.columns)} coluna(s)")
    return df

def normalize_datetime_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    logging.info("Convertendo colunas para datetime...")
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True).dt.tz_convert('America/Sao_Paulo')
    logging.info("Colunas convertidas!")
    return df

def drop_redundant_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Remove colunas redundantes geradas pelo merge
    cols_to_drop = ["character_username", "device_username"]
    df = df.drop(columns=cols_to_drop, errors="ignore")
    logging.info(f"Colunas redundantes removidas. Restam: {list(df.columns)}")
    return df

def data_transformations(users: list, characters: list, devices: list) -> pd.DataFrame:
    logging.info("Iniciando transformações...")
    df = create_dataframe_from_api(users, characters, devices)
    df = normalize_datetime_columns(df, ["created_at", "character_created_at", "device_created_at"])
    df = drop_redundant_columns(df)
    logging.info("Transformações concluídas!")
    return df