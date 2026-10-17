"""Download IEEE-CIS training inputs through the user's authenticated Kaggle CLI.

Accept the competition rules at Kaggle first. Credentials are never printed.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import zipfile

FILES = ('train_transaction.csv', 'train_identity.csv')

def extract_training_csvs(destination):
    """Extract only the two expected basenames, without trusting archive paths."""
    destination = Path(destination)
    for archive in sorted(destination.glob('*.zip')):
        with zipfile.ZipFile(archive) as z:
            for filename in FILES:
                target = destination / filename
                if target.is_file():
                    continue
                members = [m for m in z.infolist() if not m.is_dir() and Path(m.filename).name == filename]
                if len(members) > 1:
                    raise ValueError(f'Ambiguous {filename} in {archive.name}')
                if members:
                    temporary = target.with_suffix('.csv.part')
                    try:
                        with z.open(members[0]) as source, temporary.open('wb') as output:
                            shutil.copyfileobj(source, output)
                        temporary.replace(target)
                    finally:
                        temporary.unlink(missing_ok=True)
    return [name for name in FILES if not (destination / name).is_file()]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', type=Path, default=Path(__file__).parent/'data/raw/ieee_cis')
    p.add_argument('--extract-only', action='store_true', help='Extract already downloaded ZIPs without Kaggle access')
    a = p.parse_args()
    a.destination.mkdir(parents=True, exist_ok=True)
    missing = extract_training_csvs(a.destination)
    if missing and not a.extract_only:
        cli = shutil.which('kaggle')
        if not cli:
            p.exit(1, 'Install the optional Kaggle CLI: python -m pip install kaggle\nThen authenticate locally and accept https://www.kaggle.com/competitions/ieee-fraud-detection/rules\n')
        for name in missing:
            result = subprocess.run([cli, 'competitions', 'download', '-c', 'ieee-fraud-detection', '-f', name, '-p', str(a.destination)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode:
                p.exit(1, 'Kaggle download failed. Check local Kaggle authentication, network access, and acceptance of the competition rules. No credentials or CLI output were logged.\n')
        missing = extract_training_csvs(a.destination)
    if missing:
        p.exit(1, 'Missing: '+', '.join(missing)+'\nDownload from https://www.kaggle.com/competitions/ieee-fraud-detection/data\n')
    print('Training CSVs ready in:', a.destination.resolve())
    print('Set notebook DATA_DIR to this directory. Raw data is excluded from Git.')

if __name__ == '__main__':
    main()
