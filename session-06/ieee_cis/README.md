# BestAgroLab — IEEE-CIS Fraud Detection
**From Kreo Digital**

This is the selected main modelling track. The original generated-data workshop remains available as a separate graph-pattern introduction.

## Get the data

Visit https://www.kaggle.com/competitions/ieee-fraud-detection and accept the competition rules yourself. Download `train_transaction.csv` and `train_identity.csv` into a local directory. Do not commit these files, Kaggle credentials or derived row-level exports to GitHub. The competition rules specify non-commercial educational/research uses; public availability does not mean unrestricted reuse.

With an authenticated Kaggle CLI, after accepting the rules:

```bash
kaggle competitions download -c ieee-fraud-detection -f train_transaction.csv -p data/raw/ieee_cis
kaggle competitions download -c ieee-fraud-detection -f train_identity.csv -p data/raw/ieee_cis
```

Extract any downloaded ZIPs. Install the parent folder's requirements, then run from the parent folder:

```bash
python ieee_cis/run_ieee.py --data-dir data/raw/ieee_cis --limit 60000
# Larger run, after checking runtime/memory:
python ieee_cis/run_ieee.py --data-dir data/raw/ieee_cis --limit 0
```

The limit selects the earliest chronological transactions, not a random balanced sample. Class prevalence and network coverage may differ from the full dataset. Both input CSVs are initially loaded in full, so limiting the experiment does not bound ingestion memory.

## Correct graph interpretation

The target is transaction-level `isFraud`. Transaction and identity files are left-joined on `TransactionID`; many transactions have no identity row. `TransactionDT` is a relative time offset, not a calendar date.

This dataset supports a **transaction–attribute incidence graph**, not a known account-to-account payment network:

| Node type | Construction | Interpretation |
|---|---|---|
| Transaction | TransactionID | Observation to score |
| Card-attribute proxy | Exact tuple of card1–card6 when complete | Shared anonymized card characteristics; not a unique card/customer ID |
| Device attribute | DeviceInfo | Shared device description; not a hardware fingerprint |
| Email domain | P_emaildomain | Broad contextual relationship, not a shared email address |

Missing values create no edges; they must not connect all missing observations into one entity. Common domains or device models can create huge benign hubs. Equal attribute values do not establish shared ownership. The card tuple uses structured JSON encoding to avoid delimiter collisions.

No transfer rings, money-flow fan-in/out, true device ownership, IP nodes, or confirmed customer identities are claimed. Such exercises remain in the synthetic mini-lab. Here, “degree” means the number of linked transactions sharing an attribute.

## Workshop sequence — approximately four hours

1. **Data audit:** verify unique IDs, left-join cardinality, missingness and class imbalance. Review relative time ordering.
2. **Graph construction:** inspect `edges.parquet`; count nodes by kind and high-degree attribute hubs. Do not materialize all transaction pairs for a popular email domain.
3. **Historical features:** calculate the number of earlier transactions sharing each attribute within seven days. The SQL window ends one second before the current offset, excluding the current transaction and all tied-time peers.
4. **Supervised baseline:** histogram gradient boosting with amount and missingness indicators. This deliberately small baseline is not an exhaustive IEEE-CIS model.
5. **Graph-enriched supervised model:** add historical card-proxy, device-description and domain counts. These counts are local graph degree features, not a GNN or community detector.
6. **Unsupervised model:** Isolation Forest using only the transaction baseline inputs. Map scores using the training empirical distribution, without treating anomalies as fraud probabilities.
7. **Hybrid scoring:** logistic stacking of rule, supervised and anomaly signals; compare with an ensemble that also includes graph features/risk. Fit stacking only on calibration data.
8. **Evaluation:** compare average precision, Brier score and precision/recall at the same global top-100 review budget. Remove each graph attribute family in turn to measure its incremental value.

The amount rule uses the training 95th percentile. The graph-risk indicator is a training-referenced rank of historical activity. Both are illustrative; activity is not inherently suspicious. The graph ensemble may perform worse, especially if common attributes dominate. Report measured results without assuming improvement.

## Time protocol and limitations

Distinct time offsets define chronological 60/20/20 train/calibration/test partitions. All rows at a boundary timestamp stay together. Feature computation is an online replay: earlier transactions in calibration/test may become unlabelled history for later transactions. No current/future events or labels enter the graph features. Models and normalization references fit only on training; ensemble fitting uses calibration; final metrics use test.

Actual event-arrival and label-confirmation times are not supplied by this track. The runner assumes earlier observations arrive immediately and labels are available at fitting. It cannot verify realistic label-delay leakage. Add an explicit delay/embargo sensitivity experiment before treating this as a deployment simulation. Identity-field availability at transaction time is also an assumption.

Recurring proxies may cross temporal splits intentionally, reflecting known-entity replay. For a cold-start experiment, separately hold out proxy groups and report the network-coverage impact; a temporal split alone does not establish unseen-entity performance.

The official Kaggle test data has no public labels. This runner evaluates a later slice of the labelled training files. It does not claim leaderboard performance or generate a Kaggle submission.

## Optional DuckPGQ exercise

Use DuckDB 1.4.4 with a compatible DuckPGQ build. Treat transaction vertices and typed attribute vertices as a bipartite graph; use composite `(kind,value)` keys or collision-safe serialization. Match transaction → attribute ← earlier transaction and add strict temporal constraints. Validate counts against the historical SQL windows. Run graph queries on per-cutoff filtered snapshots, never the full future-inclusive incidence graph.

This native graph extension task is optional and not execution-verified. The reference modelling pipeline needs only DuckDB SQL.

## Validation status

The script is checked with generated schema-compatible fixture data, including tied timestamps and missing identity values. This verifies mechanics, not performance on IEEE-CIS. The Kaggle files have not been downloaded, and no IEEE-CIS model metrics are claimed. The fixture is independent synthetic test data, not a redistributed Kaggle extract.

Official references:
- Data dictionary: https://www.kaggle.com/competitions/ieee-fraud-detection/data
- Rules: https://www.kaggle.com/competitions/ieee-fraud-detection/rules
