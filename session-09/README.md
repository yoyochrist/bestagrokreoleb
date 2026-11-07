# Session 09 — MLflow Best Practices & Scaling

One integrated **Kreo Digital** classroom lab using generated, seeded, fraud-like synthetic data. No Kaggle credentials are required. The lab teaches experiment tracking, reproducibility, model selection, registry aliases, governance, and scaling considerations. It is not a production fraud model.

## Contents

- [Integrated notebook](Kreo_Digital_Session_09_MLflow_Best_Practices.ipynb)
- [Python dependencies](requirements.txt)
- [Optional local multi-service Compose stack](docker-compose.yml)
- [Sample local environment](.env.example)

## Quick start: notebook only

Python 3.11+:

```bash
cd session-09
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
jupyter lab Kreo_Digital_Session_09_MLflow_Best_Practices.ipynb
```

By default, the notebook tracks to `sqlite:///mlflow.db` and local artifact storage. To browse that data, start `mlflow ui --backend-store-uri sqlite:///mlflow.db` in this directory, then visit http://127.0.0.1:5000. Run cells top-to-bottom.

## Optional: Docker learning architecture

```bash
cp .env.example .env
docker compose up -d --build
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
# Restart the notebook kernel, then Run All
```

Local services: PostgreSQL metadata, MinIO S3-compatible artifacts, one MLflow tracking server. MinIO console: http://127.0.0.1:9001. Credentials are **demo only**. The Compose stack does not include TLS, identity, multi-AZ resilience or remote access. Do not deploy publicly or use real customer data.

**Why a single tracking server?** Horizontal replicas require a separate deployment layer (e.g. Kubernetes), shared backend/artifact stores, secure ingress, DB connection tuning, load tests, retention, and observability. This notebook teaches architecture design rather than pretending Docker Compose provides HA.

## Experiment methodology

- Seeded 8,000-row synthetic imbalanced classification problem with no external dataset.
- Stratified 60/20/20 train/validation/test.
- Pipelines fit preprocessing on the training split only.
- Validation PR-AUC chooses Logistic Regression vs Random Forest; test used once after selection.
- Log run parameters, evaluation metrics, version metadata, manifest artifact, input/output signature and MLflow model.
- Register selected model and attach `candidate` alias (not `champion` / deploy).
- Investigate production practices: credential management, data lineage, retention, artifact store, PostgreSQL, registry gates, backups, scaling, and failure modes.

## Limitations

Actual model metrics are not included as claims here; run the notebook to obtain results in your environment. Registration is not production readiness. The example does not implement RBAC, CI pipelines, SSO, secrets management, monitoring, database backups, or multi-replica MLflow. Do not interpret synthetic results as fraud-detection performance.

## Documentation

- https://mlflow.org/docs/latest/tracking/server/
- https://mlflow.org/docs/latest/model-registry/
- https://mlflow.org/docs/latest/self-hosting/architecture/backend-store/
- https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/
