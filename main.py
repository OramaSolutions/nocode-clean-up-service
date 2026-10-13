"""Runs the NOCODE cleanup once.

    python3 main.py             find the eligible versions and delete their data
    python3 main.py --dry-run   only list the versions that would be cleaned

Settings come from .env (see example.env). The result is printed as JSON
(status / error / message / data); the exit code is 0 on success, 1 otherwise.
"""

import argparse
import json
import sys

from service import run_cleanup
from utils.response import Status


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean up intermediate data of finished NOCODE project versions.")
    parser.add_argument("--dry-run", action="store_true", help="only list the versions that would be cleaned")
    args = parser.parse_args()

    result = run_cleanup(dry_run=args.dry_run)
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.status == Status.SUCCESS else 1


if __name__ == "__main__":
    sys.exit(main())
