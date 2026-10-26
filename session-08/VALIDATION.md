# Session 08 — Actual PaySim execution

Validated on 26 October 2026 (Asia/Jakarta).

## Execution evidence

- Executed all ten code cells, including the student response cell, in a live local Jupyter kernel through nbclient. Every required code cell completed without a cell error. Wall time: 200.0 seconds, including kernel startup, imports, full CSV validation, six training runs, evaluation and plotting.
- Actual PaySim CSV reused from Session 7: `PS_20174392719_1491204439457_log.csv`.
- SHA-256: `16910f90577b0d981bf8ff289714510bb89bc71bff7d3f220f024e287e4eea6b`.
- Scanned and schema-validated all 6,362,620 rows; modeled a fixed label-independent uniform sample of 50,000, seed 42. No generated substitute data was used for these metrics.
- Python 3.12.11; NumPy 2.3.5, pandas 2.2.3, matplotlib 3.10.8, nbformat 5.11.1 and nbclient 0.11.0. Core versions match requirements.txt.
- Source notebook schema and code compilation passed. The source has outputs cleared; the completed notebook is local at `outputs/Session_08_executed.ipynb`.
- Nine automated tests passed: all four rewards; feasible capacity and terminal stepping; invalid inputs; hand-calculated and terminal Q updates; next-state action masking; unseen-state/tie behavior; seeded training and frozen evaluation; short/partial windows and undefined denominators; common baseline budgets; chronological step separation and training-only amount edges. Several behaviors share one test method.
- An independent reviewer checked the notebook, tests and methodology and reported no actionable implementation defects.

## Fixed data windows and configuration

| Split | Step range | Sample rows | Complete 200-row episodes | Used rows | Excluded tail |
|---|---|---:|---:|---:|---:|
| Training | 1–281 | 30,065 | 150 | 30,000 | 65 |
| Validation | 282–355 | 10,098 | 50 | 10,000 | 98 |
| Final test | 356–718 | 9,837 | 49 | 9,800 | 37 |

All policies evaluate the same 9,800 test transactions, including 28 frauds. The excluded 37-row test tail includes two additional frauds, so these metrics do not describe all 9,837 test rows. Fixed complete episodes make capacity comparisons consistent but can exclude an atypical tail. Windows consist of consecutive sampled rows, not continuous production traffic.

Ten slots per episode; gamma 0.99; 30 training epochs; seeds 42, 43 and 44. Validation selected alpha 0.1 over 0.3 by mean undiscounted utility. Amount-bin edges and the amount threshold were fitted on training only. The threshold was 498,621.958. No final-test tuning, seed selection or model updates were performed.

## Observed final-test results

Values below are means across the three fixed seeds. Deterministic baselines repeat exactly. Noninteger fraud counts are averages over runs, not fractional transactions.

| Policy | Utility | Reviews | Frauds found | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| Q-learning | −354.67 | 88.67 | 0.67 | 0.74% | 2.38% |
| Never review | −280.00 | 0 | 0 | Undefined | 0% |
| Random | −721.00 | 490 | 2.33 | 0.48% | 8.33% |
| First available | −749.00 | 490 | 1 | 0.20% | 3.57% |
| Training amount threshold | −389.00 | 424 | 15 | 3.54% | 53.57% |
| Offline top amount (look-ahead reference) | −476.00 | 490 | 14 | 2.86% | 50% |

Q-learning utilities by seed were −364, −337 and −363 (sample SD 15.31). It reviewed 105, 78 and 83 transactions and found one, one and zero frauds. Unseen-state shares were 12.83%, 12.36% and 17.62%; those states use the documented PASS fallback. All policies and seeds had **zero budget violations**.

**This Q-learning policy is weak.** It detects little fraud and has worse declared utility than never reviewing. The amount threshold finds considerably more fraud but also has worse utility than never reviewing under the illustrative review cost and missed-fraud penalty. That is a useful lesson about class imbalance, state sparsity and reward design; it is not a reason to recommend never reviewing in a real system. The offline reference sees future amounts and is not an online policy or a utility upper bound.

## Artifacts and limits

Verified local exports: manifest and split audit; training and validation diagnostics; per-seed test metrics and aggregate summary; three Q-table NPZ files; evaluation decision trace and review queue; training, policy-comparison and capacity plots; executed notebook. All three plotted PNGs were visually inspected.

The notebook validates the source schema and checks capacity invariants; separate tests exercise tiny deterministic cases. Actual-data metrics above are distinct from those test fixtures. Source and executed notebooks were format-validated, and output checks confirm complete execution, no errors, matching checksum, aligned evaluation rows, valid Q-table shapes and accounting identities.

This run verifies live-kernel cell execution, not browser UI interaction. The optional Kaggle CLI download was not exercised: the existing CSV was reused. The temporary Python environment had expired and was recreated before testing; setup instructions use a project-local environment instead.

Reward points are invented, and training assumes immediate reliable labels for reviewed and passed transactions. Features are coarse and the state is not guaranteed Markov. Thirty epochs of replay and constant alpha do not prove convergence. Seed variation on one holdout is not a confidence interval. No conclusions about production efficacy, prevented financial losses, real label availability or deployment readiness follow from this run. No raw data, row-level exports or notebook execution outputs are intended for publication.
