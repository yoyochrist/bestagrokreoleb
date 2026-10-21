# Session 07 — actual PaySim validation

Validated on 21 October 2026 (Asia/Jakarta).

## Data and execution

- Downloaded the actual `ealaxi/paysim1` Kaggle archive through its public dataset download endpoint.
- Actual CSV: `PS_20174392719_1491204439457_log.csv`.
- SHA-256: `16910f90577b0d981bf8ff289714510bb89bc71bff7d3f220f024e287e4eea6b`.
- Scanned and validated all 6,362,620 rows against the 11-column PaySim schema.
- Modeled a label-independent uniform 50,000-row sample, seed 42, with the same random-priority chunk sampler shipped in the notebook.
- Temporal cutoff: step 355. Training uses steps <=355; holdout uses steps >355. Hour groups are not split.
- Holdout: 9,837 transactions, 30 fraud labels; prevalence 0.304971%.
- All 12 code cells executed sequentially in a single Python process, including every model, plot, SHAP call, metric and export. No generated substitute data was used.
- SHAP additive reconstruction passed for three exact Isolation Forest anomaly outputs and the scalar cluster-surrogate probability at absolute tolerance 1e-6.
- Notebook format validation and Python syntax compilation passed. Aggregate plots were generated and captured locally. GitHub outputs are cleared; rerun to produce them.
- Execution was sequential Python execution of notebook cells, not a live Jupyter kernel. Jupyter server/kernel startup and Kaggle CLI are not claimed as tested.

## Frozen-policy results

These results describe this synthetic-data sample and split, not expected production performance. Review budget = 100. Higher anomaly scores rank first. No holdout-label tuning was performed.

| Score | AP | ROC-AUC | Precision@100 | Recall@100 | Lift@100 |
|---|---:|---:|---:|---:|---:|
| Isolation Forest | 0.05051 | 0.89980 | 10% | 33.33% | 32.79 |
| Centroid distance | 0.10015 | 0.91204 | 15% | 50.00% | 49.185 |
| Fixed 70/30 hybrid | 0.07337 | 0.90835 | 10% | 33.33% | 32.79 |

Random-ranking expected precision is prevalence (0.304971%); expected recall is 100/9837 = 1.01657%. The hybrid does not beat centroid distance here. With only 30 holdout frauds, changes of a few cases materially affect recall; report that uncertainty rather than generalizing.

## Environment and publication

Python 3.12.14; NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, matplotlib 3.10.8, SHAP 0.54.1. requirements.txt pins these core versions. No raw dataset, account-name previews, generated review queue or fixture result is uploaded. Student answers remain exercises, not fabricated completed investigations.
