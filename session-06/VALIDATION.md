# Unified notebook validation — 17 October 2026

- nbformat 4.5 schema validated with nbformat.
- All required Python cells compiled and executed in notebook order in one shared Python namespace.
- Test input: 1,000 independent synthetic schema-compatible observations; no Kaggle rows used.
- 600 training, 200 calibration and 200 test rows.
- Duplicate-ID checks, left-join cardinality and null-attribute edge checks passed.
- Strict historical-count SQL matched independently computed counts for the first 20 transactions, including tied times.
- Local graph visualization and precision–recall/comparison plots completed.
- Shared-attribute multi-hop SQL, synthetic fan-in/out, ordered cycles and recursive traversal completed.
- Transaction and graph-enriched supervised models, Isolation Forest, both learned hybrid variants and fixed-weight hybrid completed.
- The fixed-weight heuristic does not report a probability-calibration Brier score.
- Calibration-selected analyst-review policy completed.
- Notebook contains 51 cells, 25 embedded questions and response cells; shipped outputs/execution counters are cleared.

A true nbclient/Jupyter kernel run was attempted with both TCP and IPC transport. Both were blocked by environment socket restrictions. The code-cell sequence was verified directly; a live-kernel execution is not claimed.

Actual IEEE-CIS metrics require downloaded competition data and have not been measured. Optional DuckPGQ statements remain documentation-based and not execution-verified. The notebook's skip branch is verified.
