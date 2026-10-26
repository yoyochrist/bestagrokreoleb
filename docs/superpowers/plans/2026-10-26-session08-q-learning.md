# Session 08 Q-Learning Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement task by task.

**Goal:** Deliver and execute one PaySim notebook teaching budgeted review selection with tabular Q-learning.

**Architecture:** Keep teaching code in one notebook. Tests load only the notebook's tagged core cell. Data preparation, training, comparison and exports run as visible lesson cells.

**Tech Stack:** Python 3.12, NumPy, pandas, matplotlib, nbformat, nbclient, JupyterLab.

**Spec:** `docs/superpowers/specs/2026-10-26-session08-q-learning-design.md`

## Global constraints

- REVIEW/PASS; 200 transactions and 10 slots per complete episode.
- Rewards +10 reviewed fraud, -1 reviewed legitimate, -10 passed fraud, 0 passed legitimate.
- Training-only transforms; step-separated train/validation/test; label-independent sample; no labels in state.
- Budget masks and zero terminal bootstrap; identical evaluation episodes for all policies.
- Preserve Session 7 edits; do not publish or push.

## Review focus

- Terminal or zero-budget transitions must not bootstrap invalid actions.
- No-fraud and no-review comparisons must report undefined ratios explicitly.
- Short splits must fail rather than silently evaluating no episodes.
- Unseen states and tied Q-values need reproducible safe behavior.
- Trailing partial windows must be reported and excluded consistently.

### Task 1: Tested learning core

Files: create `session-08/test_lesson.py`, notebook core cell.

Interfaces: `ReviewEnv(contexts, labels, budget)`, `q_update`, `choose_action`, `train_q`, `evaluate_policy`, `prepare_data`.

- [x] Write unittest cases extracting tagged `lesson-core` cell; assert capacity, reward, terminal, masking, deterministic replay, exact worked update, sparse-state fallback, split and metric edge cases.
- [x] Run `/private/tmp/bestagro-session07-venv/bin/python -m unittest discover -s session-08 -v`; observe missing notebook/core failure.
- [x] Implement notebook core and rerun to green.

### Task 2: Complete instructional notebook and setup

Files: notebook, README, requirements, root README, .gitignore.

Interfaces: core above; input CSV override via `KREO_DATA_PATH`; exports to `session-08/outputs/`.

- [x] Add concepts, worked update, data loading, 60/20/20 chronological split, training, validation selection, fixed seeds, final baselines, plots, interpretation and exercises.
- [x] Add dataset path instructions, simulation limits, selected-feedback warning and primary references.
- [x] Validate notebook schema and compile all code cells; rerun core tests.

### Task 3: Actual-data verification and review

Files: outputs (ignored), VALIDATION, plan ledger.

- [x] Execute all cells in the installed Python 3.12 kernel using nbclient; save an executed notebook separately.
- [x] Assert full-data checksum, sample size, no notebook errors, all expected exports and zero capacity violations.
- [x] Ask a fresh reviewer to inspect the notebook, tests, and methodology; resolve substantive findings and rerun affected checks.
- [x] Record results and limitations in VALIDATION and link completed notebook to user.

## Execution ledger

Ruling: Native implementation follows the user's approved request without a second execution-method approval. Work is restricted to new Session 8 files and small README/ignore additions; existing Session 7 edits are preserved. No Git mutations or publication.

Pre-flight: Task 2 consumes the tested notebook core; Task 3 executes the same cells and verifies exports. No competing implementations.


Task 1: complete — 9 tests first failed for the missing notebook core, then passed after implementation. The expired Session 7 temporary environment initially lacked importable NumPy; a fresh Python 3.12 environment was created before the meaningful red/green run.

Task 2: complete — 22-cell source notebook, setup guide, pinned core requirements, source links, root index and scoped ignore additions. Notebook schema and all code cells compile; source outputs remain cleared. Session 7 was not edited.

Task 3: complete — actual-data live-kernel run finished in 200.0 seconds; all 10 code cells completed. Output verifier checked the known PaySim hash, 6,362,620 source rows, 50,000 sampled rows, 18 final policy runs on identical 9,800 rows, all budget invariants, reward accounting, three Q-table shapes and expected exports. All three generated plots were visually inspected. VALIDATION.md records exact results and limitations.

Final review: fresh reviewer found no actionable defects in learning, leakage, baseline fairness, denominators or setup. Its missing-validation-document finding was resolved with session-08/VALIDATION.md and the verified outputs. No deferred minor findings.

Final verification: `/private/tmp/bestagro-session08-venv/bin/python /private/tmp/verify-session08.py` passed; `/private/tmp/bestagro-session08-venv/bin/python -m unittest discover -s session-08 -v` passed all 9 tests. No commit, push or publication performed.
