# Session 6 — Graph Analysis for Fintech Fraud Detection
**BestAgro Lab · Kreo Digital**

## One notebook, one lab

Open [Session_06_Graph_Fraud_Hybrid_Scoring.ipynb](Session_06_Graph_Fraud_Hybrid_Scoring.ipynb).

The complete session is now in this notebook: explanations, runnable code, graph visualization, exercises, 25 embedded questions and response cells, supervised and unsupervised models, fixed-weight and learned hybrid risk scoring, evaluation charts and analyst review.

IEEE-CIS is the main dataset throughout the modelling flow. One small synthetic transfer example explains fan-in/out, ordered cycles and bounded traversal because IEEE-CIS does not provide account-to-account transfers. It is a section within the same notebook, not a second lab or a dataset merged into training.

## Data download

[Follow the IEEE-CIS data setup guide](DATA_SETUP.md). IEEE-CIS is a Kaggle Competition; sign in and accept its rules to download the two training CSVs. An optional authenticated download/extraction helper is included.

## Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r session-06/requirements.txt
jupyter lab session-06/Session_06_Graph_Fraud_Hybrid_Scoring.ipynb
```

VS Code's Jupyter extension can also open the notebook. Select the environment with the installed dependencies. On Windows activate `.venv\Scripts\Activate.ps1` instead.

Accept the Kaggle competition rules and download/extract `train_transaction.csv` and `train_identity.csv`. Set the notebook's `DATA_DIR` to their directory. Default paths are relative to the notebook kernel's working directory; the notebook prints the resolved path. Run all cells sequentially. The first run uses the earliest 60,000 labelled transactions; set `LIMIT=0` for all rows after checking available memory.

The optional DuckPGQ section is disabled by default. Required graph analysis uses DuckDB SQL and does not need a graph extension. No Neo4j.

## Supporting files

The `ieee_cis/` and `synthetic/` folders preserve earlier CLI reference solutions. They are supporting material; learners do not need to run them separately. Their previous narrative guides are replaced by pointers to the unified notebook. Earlier stored synthetic results must not be interpreted as IEEE-CIS metrics.

## Validation

Notebook schema validated; every required code cell executed sequentially on a 1,000-row independent schema-compatible fixture, including plots, all five scoring variants and review policy. Jupyter kernel launch itself was blocked by this authoring environment's socket restrictions, so a live-kernel end-to-end run is not claimed. Actual Kaggle training and optional DuckPGQ execution remain unverified. See [VALIDATION.md](VALIDATION.md).

Keep Kaggle inputs, credentials and row-level outputs out of this public repository. Clear notebook outputs before committing a data-backed run.
