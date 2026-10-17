# Validation — 17 October 2026

Executed with Python 3.12, DuckDB 1.4.4, NumPy 2.3.5 and scikit-learn 1.8.0.

- Reference pipeline completed successfully.
- 7,200 feature rows, one per account.
- Both future and late-arriving records excluded: 1,800 total.
- Visible transfer amounts remain below 1,000.
- Time-ordered cycle detection returns matches.
- Training and calibration labels are available before their next evaluation stage.
- Final test set contains 2,000 accounts; prevalence 19.6%.
- All seven extension-free answer queries executed successfully.
- Transfer source references have no orphan accounts.
- Example review queue contains 216 accounts at the calibration-selected threshold.

| Model | Average precision | Precision@50 | Recall@50 |
|---|---:|---:|---:|
| Rules | 0.3851 | 0.66 | 0.0842 |
| Supervised | 0.7297 | 0.88 | 0.1122 |
| Hybrid without graph | 0.7362 | 0.86 | 0.1097 |
| Hybrid with graph | 0.8826 | 1.00 | 0.1276 |
| Deck fixed weights | 0.7552 | 0.96 | 0.1224 |

These are synthetic teaching results, not real fintech fraud benchmarks. The top-50 budget is global across the test period.

DuckPGQ extension installation failed because its download service could not be reached. Native graph statements were reviewed against official documentation but were not executed. PostgreSQL/AGE was not installed or tested.
