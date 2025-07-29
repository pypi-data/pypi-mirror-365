import argparse
import sys
import os
from .update_regex import Regexes

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_PATH)

def main():
    parser = argparse.ArgumentParser(prog="ua_extract", description="ua_extract CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    update_parser = subparsers.add_parser("update_regexes", help="Update regexes from upstream")
    update_parser.add_argument(
        "--path",
        default=os.path.join(ROOT_PATH, "regexes", "upstream"),
        help="Destination path to place regexes content"
    )
    update_parser.add_argument(
        "--repo",
        default="https://github.com/matomo-org/device-detector.git",
        help="Git repo URL"
    )
    update_parser.add_argument(
        "--branch",
        default="master",
        help="Git branch name"
    )
    update_parser.add_argument(
        "--sparse-dir",
        default="regexes",
        help="Sparse directory inside repo"
    )
    update_parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Deleting existing regex"
    )

    args = parser.parse_args()

    if args.command == "update_regexes":
        regexes = Regexes(
            upstream_path=args.path,
            repo_url=args.repo,
            branch=args.branch,
            sparse_dir=args.sparse_dir,
            cleanup=args.cleanup
        )
        regexes.update_regexes()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
