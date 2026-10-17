# IEEE-CIS data setup — Session 6

IEEE-CIS is a **Kaggle Competition**, not a regular Kaggle Dataset:

- [Download page](https://www.kaggle.com/competitions/ieee-fraud-detection/data)
- [Competition rules](https://www.kaggle.com/competitions/ieee-fraud-detection/rules)

Sign into Kaggle and accept the rules yourself before downloading. The source files are not stored in this repository. Do not commit Kaggle credentials or downloaded competition data.

## Option A: browser download

Download `train_transaction.csv` and `train_identity.csv`. Extract any ZIP archives and place the CSVs in `session-06/data/raw/ieee_cis/`.

If you downloaded ZIPs, the helper can extract only the required files:

```bash
python session-06/download_ieee_cis.py --extract-only
```

## Option B: authenticated Kaggle CLI

Install the optional CLI and configure authentication using Kaggle's current instructions. Keep credentials local; never paste them into notebook cells or GitHub.

```bash
python -m pip install kaggle
python session-06/download_ieee_cis.py
```

The helper downloads only the two training inputs, extracts ZIPs if needed, and prints the absolute data directory. It does not accept the rules on your behalf or bypass access requirements. Downloads require working authentication and network access.

## Configure the notebook

Set `DATA_DIR` to the absolute directory printed by the helper:

```python
DATA_DIR = Path('/absolute/path/to/bestagrokreoleb/session-06/data/raw/ieee_cis')
```

On Windows use a raw string, for example `Path(r'C:\labs\bestagrokreoleb\session-06\data\raw\ieee_cis')`.

The notebook also checks common repository/notebook working directories and `/kaggle/input/ieee-fraud-detection`. An explicit `SESSION6_DATA_DIR` environment override takes precedence and is not silently replaced.

## Troubleshooting

| Symptom | Action |
|---|---|
| Cannot find IEEE-CIS in Kaggle Datasets | Open the Competition link above |
| Kaggle requires sign-in or rule acceptance | Sign in and accept the competition rules |
| Notebook `FileNotFoundError` | Set `DATA_DIR` to the extracted CSV directory |
| CSV names end in `.zip` | Extract first, or use the helper's `--extract-only` |
| CLI authentication/download error | Check your local Kaggle authentication, rule acceptance and network |

Only the labelled training inputs are needed. Kaggle's official test files have no public labels; the notebook evaluates a later slice of the labelled training data.

Validation: helper syntax, help and local ZIP extraction checked. Authenticated Kaggle downloading has not been tested here; no dataset or Kaggle model results are claimed.
