# 🎮 Pipeline RPG

Pipeline de dados end-to-end para processamento de dados simulados de um jogo RPG, utilizando Flask, Apache Airflow, PostgreSQL, Google Cloud Storage e BigQuery.

---

## 📐 Arquitetura

```
generator/app.py (Flask API)
        │
        ▼
   extract (GET + API Key)
        │
        ▼
   transform (merge + normalização)
        │
        ├──► load (PostgreSQL - Silver)
        │
        └──► gold_to_gcs (GCS - Gold/Star Schema)
                    │
                    ▼
            gcs_to_bigquery (BigQuery - Datamart)
```

---

## 🗂️ Estrutura do Projeto

```
pipeline-rpg/
├── dags/
│   └── rpg_dags.py             # DAG do Airflow
├── generator/
│   ├── app.py                  # Flask API + geração de dados
│   ├── users.py                # Gerador de usuários
│   ├── characters.py           # Gerador de personagens
│   └── devices.py              # Gerador de dispositivos
├── src/
│   ├── extract_data.py         # Extração via API
│   ├── transform_data.py       # Transformações e merge
│   └── load_data.py            # Carga no PostgreSQL
├── data/                       # Arquivos temporários (parquet)
├── config/
│   ├── .env                    # Variáveis de ambiente
│   └── gcp-key.json            # Chave Service Account GCP
├── logs/                       # Logs do Airflow
├── plugins/                    # Plugins do Airflow
├── .env                        # Variáveis do Docker Compose
├── .gitignore
└── docker-compose.yaml
```

---

## 🛠️ Tecnologias

| Camada | Tecnologia |
|---|---|
| Geração de dados | Python, Faker, Flask |
| Orquestração | Apache Airflow 3.1.7 |
| Infraestrutura | Docker, Docker Compose |
| Silver Layer | PostgreSQL |
| Gold Layer | Google Cloud Storage (GCS) |
| Datamart | Google BigQuery |
| Modelagem | Star Schema |

---

## ⚙️ Configuração

### Pré-requisitos

- Docker Desktop
- Python 3.12+
- uv
- Google Cloud SDK (`gcloud`)
- Projeto no GCP com BigQuery e Cloud Storage habilitados

### Variáveis de Ambiente

**`.env`** (raiz — usado pelo Docker Compose):
```env
AIRFLOW_UID=50000
```

**`config/.env`** (usado pelo pipeline):
```env
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_DATABASE=pipeline_rpg
DB_HOST=host.docker.internal
API_KEY=                          # gerada automaticamente pelo app.py
FLASK_DEBUG=true
GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/config/gcp-key.json
GCS_BUCKET=pipeline-rpg-gold
GCP_PROJECT_ID=seu-projeto-gcp
```

### Dependências Python (Airflow)

No `.env` da raiz, adicione:
```env
_PIP_ADDITIONAL_REQUIREMENTS=faker sqlalchemy psycopg2-binary python-dotenv flask pandas pyarrow google-cloud-storage google-cloud-bigquery
```

---

## 🚀 Como Executar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/pipeline-rpg.git
cd pipeline-rpg
```

### 2. Configure as variáveis de ambiente
```bash
cp config/.env.example config/.env
# edite config/.env com suas credenciais
```

### 3. Coloque a chave GCP
```
config/gcp-key.json  ← Service Account com role Storage Object Admin e BigQuery Admin
```

### 4. Crie o banco de dados PostgreSQL
```bash
psql -U seu_usuario -c "CREATE DATABASE pipeline_rpg;"
```

### 5. Crie os recursos no GCP
```bash
# Bucket GCS
gcloud storage buckets create gs://pipeline-rpg-gold --location=southamerica-east1

# Permissão da Service Account
gcloud storage buckets add-iam-policy-binding gs://pipeline-rpg-gold \
  --member="serviceAccount:sua-sa@seu-projeto.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Dataset BigQuery
bq mk --dataset --location=southamerica-east1 seu-projeto:rpg_datamart
```

### 6. Suba o Airflow
```bash
docker compose up
```

### 7. Suba a API Flask (terminal separado)
```bash
uv run generator/app.py
```

### 8. Acesse o Airflow
```
http://localhost:8080
usuário: airflow
senha: airflow
```

Ative e dispare o DAG `pipeline_rpg`.

---

## 📊 Star Schema (Datamart)

```
                    ┌─────────────┐
                    │  dim_date   │
                    │─────────────│
                    │ date_id (PK)│
                    │ date        │
                    │ year        │
                    │ month       │
                    │ day         │
                    │ weekday     │
                    └──────┬──────┘
                           │
┌──────────────┐    ┌──────┴───────────────┐    ┌────────────────┐
│   dim_user   │    │  fact_player_activity │    │  dim_character │
│──────────────│    │───────────────────────│    │────────────────│
│ user_id (PK) │◄───│ activity_id (PK)      │───►│ character_id   │
│ name         │    │ user_id (FK)          │    │ character_name │
│ email        │    │ character_id (FK)     │    │ created_at     │
└──────────────┘    │ device_id (FK)        │    └────────────────┘
                    │ created_at (FK)       │
                    │ player_client         │
                    └──────────┬────────────┘
                               │
                    ┌──────────┴──────┐
                    │   dim_device    │
                    │─────────────────│
                    │ device_id (PK)  │
                    │ player_client   │
                    └─────────────────┘
```

---

## 🔍 Consultando no BigQuery

```sql
SELECT 
    f.activity_id,
    u.name,
    u.email,
    c.character_name,
    d.player_client,
    dt.date,
    dt.weekday
FROM `seu-projeto.rpg_datamart.fact_player_activity` f
JOIN `seu-projeto.rpg_datamart.dim_user`      u  ON f.user_id      = u.user_id
JOIN `seu-projeto.rpg_datamart.dim_character` c  ON f.character_id = c.character_id
JOIN `seu-projeto.rpg_datamart.dim_device`    d  ON f.device_id    = d.device_id
JOIN `seu-projeto.rpg_datamart.dim_date`      dt ON f.created_at   = dt.date
```

---

## 🔒 Segurança

- Nunca commite `config/.env` ou `config/gcp-key.json`
- Adicione `config/` ao `.gitignore`
- A `API_KEY` é gerada automaticamente pelo `app.py` no primeiro startup
- Use senhas fortes para o PostgreSQL em produção

---

## 📅 Agendamento

O DAG roda com schedule `@daily`. Para alterar, edite o parâmetro `schedule` em `dags/rpg_dags.py`.

---

## 👤 Autor

Desenvolvido como projeto de aprendizado de engenharia de dados.
