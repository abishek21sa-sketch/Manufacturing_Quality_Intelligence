from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from mqi.validation import run_validation

if __name__ == "__main__":
    run_validation()
    print("Validation evidence regenerated successfully.")
