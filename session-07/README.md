# Kreo Digital Session 07 — PaySim: Unsupervised Learning & SHAP Values

Open [the single integrated notebook](Kreo_Digital_Session_07_Unsupervised_SHAP.ipynb).

PaySim replaces the restricted bank-account competition at the user's request. The same coherent Session 07 lab covers EDA, preprocessing, K-Means, cluster profiling, PCA, bounded DBSCAN, Isolation Forest, direct anomaly-score SHAP, cluster-surrogate explanations, held-out fraud evaluation and optional 70/30 hybrid ranking. Exercises, critical-thinking questions, case investigations and an assessment rubric are inside the notebook.

## Start

Python 3.12 recommended. From repository root:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r session-07/requirements.txt
cd session-07
kaggle datasets download -d ealaxi/paysim1 -p data --unzip
jupyter lab Kreo_Digital_Session_07_Unsupervised_SHAP.ipynb
```

Alternatively download [PaySim on Kaggle](https://www.kaggle.com/datasets/ealaxi/paysim1) manually and extract the CSV to `session-07/data/`. The original filename is `PS_20174392719_1491204439457_log.csv`. Set `KREO_DATA_PATH` to another absolute CSV path before launching Jupyter if necessary. Select the installed environment as the kernel, then restart and run all cells.

## Dataset and methodology

The actual PaySim file has 11 columns and 6,362,620 simulated mobile-money transactions. The loader validates every chunk and draws a fixed, label-independent uniform sample of 50,000 rows across the complete file. It does not take a chronological prefix or oversample fraud. This scan takes time but keeps memory bounded. `MAX_ROWS=None` loads everything and requires substantially more memory.

Transactions above the 80th percentile of sampled step values form the temporal holdout, with all rows at a given step on the same side. Baseline inputs are transaction type, log amount and cyclical hour of day. Account names, labels, absolute step and existing rule flag are excluded. All four balance fields are excluded because the provider cautions that canceled fraud handling can affect balances. No balance-error shortcuts, graph edges or demographic attributes are invented.

Preprocessing, K selection and hybrid weights use no fraud labels. Labels are revealed only for final evaluation. SHAP explains exactly `-IsolationForest.score_samples`; additive reconstruction is checked. Anomaly and hybrid scores are not calibrated fraud probabilities. Weak fraud lift is a valid result with this conservative feature set.

## Expected deliverables

Run all cells, answer the embedded exercises, and complete three case notes and the review queue. The notebook exports an input hash/version manifest, training feature audit, cluster profiles, holdout enrichment, AP/ROC-AUC/precision-recall/lift metrics, three waterfall plots, case attributions and a 100-transaction review queue into `outputs/`. Explanations cover only three cases, not the entire queue.

The GitHub notebook has outputs cleared; actual-data validation and aggregate results are recorded in [VALIDATION.md](VALIDATION.md). Local execution produces the plots and results. No dataset, credentials or row-level export is uploaded.

## Validation

See [VALIDATION.md](VALIDATION.md) for actual-data execution scope and limitations. Core package versions in requirements.txt match the validation environment. A live Jupyter-kernel run is distinct from sequential execution of its cells; no unsupported kernel claim is made.
