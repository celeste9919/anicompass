"""Create and append structured AniCompass daily development logs."""

from __future__ import annotations

import argparse
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "dev-logs"


def current_date() -> str:
    return datetime.now().astimezone().date().isoformat()


def current_time() -> str:
    return datetime.now().astimezone().strftime("%H:%M:%S %z")


def ensure_log(date_text: str) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"{date_text}.md"
    if not path.exists():
        path.write_text(
            "\n".join(
                [
                    f"# Development Log: {date_text}",
                    "",
                    "## Day Goal",
                    "",
                    "- Not set",
                    "",
                    "## Sessions",
                    "",
                    "## End Of Day",
                    "",
                    "### Completed",
                    "",
                    "- None",
                    "",
                    "### Remaining",
                    "",
                    "- None",
                    "",
                    "### Risks Or Blockers",
                    "",
                    "- None",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return path


def git_snapshot() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def add_section(lines: list[str], title: str, values: list[str] | None) -> None:
    if not values:
        return
    cleaned = [value.strip() for value in values if value.strip()]
    if not cleaned:
        return
    lines.extend(["", f"#### {title}", ""])
    lines.extend(f"- {value}" for value in cleaned)


def append_session(args: argparse.Namespace) -> Path:
    path = ensure_log(args.date)
    lines = ["", f"### Session {current_time()}"]
    add_section(lines, "Completed", args.done)
    add_section(lines, "Checks", args.check)
    add_section(lines, "Decisions", args.decision)
    add_section(lines, "Blockers", args.blocker)
    add_section(lines, "Todo", args.todo)

    if args.git_snapshot:
        changes = git_snapshot()
        add_section(lines, "Git Snapshot", changes or ["No changed files detected"])

    if len(lines) == 2:
        raise SystemExit("Nothing to append. Provide at least one log item.")

    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    ensure_parser = subparsers.add_parser("ensure", help="Create today's log")
    ensure_parser.add_argument("--date", default=current_date())

    add_parser = subparsers.add_parser("add", help="Append a session entry")
    add_parser.add_argument("--date", default=current_date())
    add_parser.add_argument("--done", action="append")
    add_parser.add_argument("--check", action="append")
    add_parser.add_argument("--decision", action="append")
    add_parser.add_argument("--blocker", action="append")
    add_parser.add_argument("--todo", action="append")
    add_parser.add_argument(
        "--git-snapshot",
        action="store_true",
        help="Append current short git status without file contents",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "ensure":
        path = ensure_log(args.date)
    else:
        path = append_session(args)
    print(path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()


