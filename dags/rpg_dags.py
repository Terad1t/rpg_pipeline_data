@task
def gold_to_gcs():
    import pandas as pd
    from google.cloud import storage

    bucket_name = os.getenv('GCS_BUCKET')
    df = pd.read_parquet('/opt/airflow/data/rpg_data.parquet')

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

    client = storage.Client()  # ← cliente GCS
    bucket = client.bucket(bucket_name)

    for blob_name, table_df in tables.items():
        csv_bytes = table_df.to_csv(index=False).encode('utf-8')
        blob = bucket.blob(blob_name)
        blob.upload_from_string(csv_bytes, content_type='text/csv')
        print(f"Enviado: gs://{bucket_name}/{blob_name} ({len(table_df)} linhas)")

@task
def gcs_to_bigquery():
    from google.cloud import bigquery  # ← cliente BigQuery separado

    project_id  = os.getenv('GCP_PROJECT_ID')
    bucket_name = os.getenv('GCS_BUCKET')
    client      = bigquery.Client(project=project_id)

    tables = [
        'dim_user',
        'dim_character',
        'dim_device',
        'dim_date',
        'fact_player_activity',
    ]

    for table in tables:
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        uri       = f"gs://{bucket_name}/gold/{table}.csv"
        table_ref = f"{project_id}.rpg_datamart.{table}"

        load_job = client.load_table_from_uri(
            uri, table_ref,
            job_config=job_config,
            location="southamerica-east1"
        )
        load_job.result()
        print(f"Carregado: {table_ref}")

# ── Fluxo ──
api  = start_api()
data = extract()
api >> data
transform(data) >> load() >> gold_to_gcs() >> gcs_to_bigquery()