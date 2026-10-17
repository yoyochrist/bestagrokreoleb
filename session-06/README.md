# Session 6 — Graph Analysis for Fintech Fraud Detection
**BestAgro Lab · Kreo Digital**

Extend supervised and unsupervised detection with graph context while retaining one hybrid scoring layer. Uses DuckDB; no Neo4j.

## Main track: IEEE-CIS

Start with [the IEEE-CIS workbook](ieee_cis/README.md). The target is transaction-level `isFraud`. The graph connects transactions to shared anonymized attributes; it does not assert unique customers, hardware fingerprints or money-transfer flows.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r session-06/requirements.txt
python session-06/ieee_cis/run_ieee.py --data-dir data/raw/ieee_cis --output-dir outputs/ieee_cis --limit 60000
```

Download the two training CSVs after accepting the Kaggle competition rules; see the workbook. Data, credentials and row-level IEEE-CIS outputs are not committed.

## Introductory track: synthetic transfer graphs

Use [the synthetic workbook](synthetic/README.md) for fan-in/out, ordered payment cycles, device sharing and multi-hop traversal. These scenarios are separate from IEEE-CIS because it does not supply the necessary transfer endpoints or unique device IDs.

```bash
python session-06/synthetic/run_lab.py
```

The runner regenerates its CSV data and DuckDB database locally. Its stored results are explicitly synthetic, not IEEE-CIS results.

## Session outcomes

1. Construct graph representations and inspect ambiguous shared attributes.
2. Compute strictly historical graph features.
3. Compare supervised, unsupervised and graph-enriched detection.
4. Combine signals using hybrid scoring.
5. Evaluate on later observations at the same review budget.
6. Explain limitations, temporal leakage and false positives.

## Verification

- Synthetic DuckDB SQL/ML pipeline executed successfully, including all seven answer queries.
- IEEE-CIS runner passed a 1,000-row independent synthetic fixture; actual Kaggle training has not been run.
- DuckPGQ extension installation was blocked by connectivity. Native graph SQL is provided as an optional, unverified exercise.
- See each track's `VALIDATION.md` for details.

## Package history

This initial Session 6 import includes both deliverables prepared on 17 October 2026: the original graph-analysis workshop and the later IEEE-CIS modelling update. The repository was empty before this import; there was no previous remote commit to preserve beyond initialization.
