# Session 08 — Q-Learning for Fraud Review

Open [the integrated notebook](Kreo_Digital_Session_08_Q_Learning_Fraud_Review.ipynb). Learn to choose **REVIEW** or **PASS** while preserving capacity for later transactions. Each episode contains 200 transactions and ten review slots.

The lesson includes an inspectable NumPy Q-table, a hand-calculated Bellman update, epsilon-greedy training, validation-based parameter selection, six policy comparisons, decision traces, exercises, three analyst case notes and an assessment rubric. No RL framework is required. Suggested classroom time: 2–3 hours.

## Run

Use Python 3.12. From the repository root:

```bash
python3.12 -m venv .venv-session08
source .venv-session08/bin/activate
# Windows PowerShell: .venv-session08\Scripts\Activate.ps1
python -m pip install -r session-08/requirements.txt
python -m ipykernel install --prefix "$VIRTUAL_ENV" --name session08 --display-name "Session 8 (Python 3.12)"
cd session-08
jupyter lab Kreo_Digital_Session_08_Q_Learning_Fraud_Review.ipynb
```

Select **Session 8 (Python 3.12)**, then **Kernel → Restart Kernel and Run All Cells**. The first scan validates all 6,362,620 PaySim rows and samples 50,000 without consulting fraud labels. It then trains two alpha candidates with three fixed seeds. Runtime depends on your machine; actual measured runtime is recorded in [VALIDATION.md](VALIDATION.md).

## Dataset

The notebook first reuses `../session-07/data/PS_20174392719_1491204439457_log.csv`. It also accepts that filename in `session-08/data/`, or an absolute path supplied before launching Jupyter:

```bash
export KREO_DATA_PATH="/absolute/path/PS_20174392719_1491204439457_log.csv"
```

If needed, download [PaySim from Kaggle](https://www.kaggle.com/datasets/ealaxi/paysim1) and extract the CSV into `session-08/data/`. An optional Kaggle CLI download, from the repository root, is:

```bash
python -m pip install 'kaggle>=1.6,<2'
kaggle datasets download -d ealaxi/paysim1 -p session-08/data --unzip
```

Authenticate locally if the CLI requires it. Keep credentials and raw data out of Git. New-session data, environments and generated outputs are ignored.

## What is simulated

PaySim is simulated transaction data. Our environment adds illustrative utility points: reviewed fraud +10, legitimate review −1, passed fraud −10, passed legitimate 0. Reviewing does not guarantee that loss is prevented. The training simulator assumes immediate reliable labels after **all** actions, including PASS. This is much stronger feedback than most production review systems provide.

Only transaction type, training-fitted amount bin, remaining capacity and episode position enter the state. Account names, balances, labels and existing fraud flags are excluded. Splits are chronological 60/20/20 by complete step groups; transforms use training only. Incomplete 200-row windows are dropped consistently and reported. These are windows of sampled rows, not a continuous operational stream.

Validation chooses alpha using mean undiscounted utility across three predeclared seeds. Final policies are frozen, with no exploration or Q-table updates. Comparisons include never-review, random, first-available, training-fitted amount threshold and a clearly labeled **offline top-amount look-ahead reference**. Q-learning optimizes discounted return; evaluation also reports undiscounted utility, reviews, precision, recall, missed fraud, state coverage and budget violations. No performance advantage is promised.

## Outputs and checks

Local `outputs/` contains the source hash and experiment manifest, split audit, learning curves, validation and final metrics, three Q-tables, policy comparison and capacity plots, decision trace and review queue. Generated row-level traces contain evaluation labels; they are not policy inputs. Student case notes remain exercises to complete.

The source notebook is saved without outputs. A verified local execution is available as `outputs/Session_08_executed.ipynb` after validation.

```bash
# From repository root, in the environment above:
python -m unittest discover -s session-08 -v
```

These tests extract the notebook's `lesson-core` cell and verify rewards, legal actions, terminal updates, budget accounting, deterministic training, frozen evaluation, split separation and undefined metric denominators. See [VALIDATION.md](VALIDATION.md) for actual-data execution evidence and limitations.
