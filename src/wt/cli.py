from __future__ import annotations

import argparse
import sys

from wt.commands.create import run_create
from wt.commands.list import run_list
from wt.commands.remove import run_remove
from wt.commands.restore import run_restore
from wt.errors import UserFacingError
from wt.services.prompts import PromptIO
from wt.services.repo import discover_repo_context

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wt")
    subparsers = parser.add_subparsers(dest="command", required=True)
    parser._subparsers = subparsers  # type: ignore[attr-defined]

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--branch")
    create_parser.add_argument("--yes", action="store_true")

    subparsers.add_parser("list")

    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("--branch")
    remove_parser.add_argument("--yes", action="store_true")

    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("--branch")
    restore_parser.add_argument("--yes", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        context = discover_repo_context()
        prompts = PromptIO()

        if args.command == "create":
            message = run_create(context, prompts, getattr(args, "branch", None), getattr(args, "yes", False))
        elif args.command == "list":
            message = run_list(context)
        elif args.command == "remove":
            message = run_remove(context, prompts, getattr(args, "branch", None), getattr(args, "yes", False))
        else:
            message = run_restore(context, prompts, getattr(args, "branch", None), getattr(args, "yes", False))
    except UserFacingError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if message:
        print(message)
    return 0
