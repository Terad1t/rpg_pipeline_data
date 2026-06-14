from datetime import datetime, timedelta
from airflow.sdk import dag, task
from pathlib import Path
import sys, os

sys.path.insert(0, '/opt/airflow/src')

from extract_data import extract_all
from transform_data import data_transformations
from load_data import load_rpg_data
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)

@dag(
    dag_id='pipeline_rpg',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5)
    },
    description="Pipeline RPG - users, characters, devices",
    schedule='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['rpg']
)
def rpg_pipeline():

    @task
    def start_api():
        import subprocess
        import time
        subprocess.Popen(["python", "/opt/airflow/generator/app.py"])
        time.sleep(3)

    @task
    def extract():
        data = extract_all()
        return data

    @task
    def transform(data: dict):
        df = data_transformations(
            users=data["users"],
            characters=data["characters"],
            devices=data["devices"]
        )
        df.to_parquet('/opt/airflow/data/rpg_data.parquet', index=False)

    @task
    def load():
        import pandas as pd
        df = pd.read_parquet('/opt/airflow/data/rpg_data.parquet')
        load_rpg_data('rpg_players', df)

    @task
    def gold_to_gcs():
        import pandas as pd
        from google.cloud import storage

        bucket_name = os.getenv('GCS_BUCKET')
        df = pd.read_parquet('/opt/airflow/data/rpg_data.parquet')
        print(df.columns.tolist())

        dim_user = df[['id', 'name', 'email']].drop_duplicates().rename(columns={'id': 'user_id'})

        dim_character = df[['character_id', 'character_name', 'character_created_at']].drop_duplicates()

        dim_device = df[['device_id_x', 'player_client']].drop_duplicates().rename(columns={'device_id_x': 'device_id'})

        dim_date = df[['character_created_at']].drop_duplicates().rename(columns={'character_created_at': 'date'})
        dim_date['date']    = pd.to_datetime(dim_date['date'])
        dim_date['year']    = dim_date['date'].dt.year
        dim_date['month']   = dim_date['date'].dt.month
        dim_date['day']     = dim_date['date'].dt.day
        dim_date['weekday'] = dim_date['date'].dt.day_name()
        dim_date.insert(0, 'date_id', range(1, len(dim_date) + 1))

        fact = df[['id', 'character_id', 'device_id_x', 'character_created_at', 'player_client']].copy()
        fact = fact.rename(columns={
            'id': 'user_id',
            'device_id_x': 'device_id',
            'character_created_at': 'created_at'
        })
        fact.insert(0, 'activity_id', range(1, len(fact) + 1))

        tables = {
            'gold/dim_user.csv':             dim_user,
            'gold/dim_character.csv':        dim_character,
            'gold/dim_device.csv':           dim_device,
            'gold/dim_date.csv':             dim_date,
            'gold/fact_player_activity.csv': fact,
        }

        client = storage.Client()
        bucket = client.bucket(bucket_name)

        for blob_name, table_df in tables.items():
            csv_bytes = table_df.to_csv(index=False).encode('utf-8')
            blob = bucket.blob(blob_name)
            blob.upload_from_string(csv_bytes, content_type='text/csv')
            print(f"Enviado: gs://{bucket_name}/{blob_name} ({len(table_df)} linhas)")

    api = start_api()
    data = extract()
    api >> data
    transform(data) >> load() >> gold_to_gcs()

rpg_pipeline()