from __future__ import annotations
import argparse, json
from mqi.validation import run_validation


def main():
    p = argparse.ArgumentParser(prog="mqi")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bootstrap", help="Generate demo data, train model, and create validation evidence")
    b.add_argument("--rows", type=int, default=5000)
    sub.add_parser("validate", help="Run the reproducible validation suite")
    args = p.parse_args()
    if args.cmd == "bootstrap":
        print(json.dumps(run_validation(args.rows), indent=2))
    elif args.cmd == "validate":
        print(json.dumps(run_validation(), indent=2))

if __name__ == "__main__":
    main()
