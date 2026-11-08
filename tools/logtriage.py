"""Summarize Civ 6 log errors by mod.

Reads Database.log, Modding.log, Lua.log and GameEffects.log from a log
folder, pulls out error and warning lines, groups repeats, and guesses
which mod each one came from by looking for a mod folder in the line
or in the lines just before it.

Usage:
    python tools/logtriage.py <logdir> [--out docs/playtests/NNN-triage.md]

Source: custom (SPEC section 5, tools table).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

LOG_FILES = ("Database.log", "Modding.log", "Lua.log", "GameEffects.log")

# How far back to look for a file path when the error line has none.
CONTEXT_LINES = 3

ERROR_PATTERNS = {
    "Database.log": re.compile(r"\bERROR\b|constraint failed|no such (table|column)|syntax error", re.I),
    "Modding.log": re.compile(r"\b(error|failed|failure|missing|could not|unable to)\b", re.I),
    "Lua.log": re.compile(r"runtime error|syntax error|attempt to|stack traceback|\berror\b", re.I),
    "GameEffects.log": re.compile(r"\b(error|warning|invalid|missing)\b", re.I),
}

WARNING_WORDS = re.compile(r"\bwarning\b", re.I)

# Lines that match an error pattern but aren't errors.
IGNORE_PATTERNS = re.compile(
    r"0 errors|no errors|errors: 0|ErrorHandler|LoadError=0|OnError",
    re.I,
)

TIMESTAMP = re.compile(r"^\s*\[\s*[\d.:]+\s*\]\s*")

# A mod folder inside the local Mods folder or the Workshop content folder.
MOD_PATH = re.compile(
    r"(?:[\\/]Mods[\\/]|[\\/]289070[\\/])([^\\/:*?\"<>|\r\n]+)",
    re.I,
)
# Base game and DLC paths.
GAME_PATH = re.compile(r"[\\/](Base|DLC[\\/][^\\/]+)[\\/]", re.I)

UNKNOWN = "(unknown source)"
BASE = "(base game / DLC)"


@dataclass
class Issue:
    log: str
    severity: str
    message: str
    source: str
    count: int = 1
    first_line: int = 0


@dataclass
class Report:
    issues: "OrderedDict[tuple, Issue]" = field(default_factory=OrderedDict)
    missing_logs: list[str] = field(default_factory=list)
    lines_read: dict[str, int] = field(default_factory=dict)

    def add(self, issue: Issue) -> None:
        key = (issue.log, issue.source, issue.message)
        if key in self.issues:
            self.issues[key].count += 1
        else:
            self.issues[key] = issue

    def by_source(self) -> "OrderedDict[str, list[Issue]]":
        grouped: "OrderedDict[str, list[Issue]]" = OrderedDict()
        for issue in sorted(self.issues.values(), key=lambda i: (i.source == UNKNOWN, i.source.lower())):
            grouped.setdefault(issue.source, []).append(issue)
        return grouped


def strip_timestamp(line: str) -> str:
    return TIMESTAMP.sub("", line).strip()


def find_source(text: str) -> str | None:
    match = MOD_PATH.search(text)
    if match:
        return match.group(1).strip()
    if GAME_PATH.search(text):
        return BASE
    return None


def is_issue(log: str, line: str) -> bool:
    if IGNORE_PATTERNS.search(line):
        return False
    return bool(ERROR_PATTERNS[log].search(line))


def triage_lines(log: str, lines: list[str], report: Report) -> None:
    recent: list[str] = []
    last_source: str | None = None
    for number, raw in enumerate(lines, start=1):
        line = strip_timestamp(raw)
        if not line:
            continue
        here = find_source(line)
        if is_issue(log, line):
            source = here
            if source is None:
                for previous in reversed(recent):
                    source = find_source(previous)
                    if source:
                        break
            if source is None and log == "Modding.log":
                # Modding.log names the component being applied before it fails.
                source = last_source
            severity = "warning" if WARNING_WORDS.search(line) else "error"
            report.add(Issue(log, severity, line, source or UNKNOWN, first_line=number))
        if here:
            last_source = here
        recent.append(line)
        if len(recent) > CONTEXT_LINES:
            recent.pop(0)


def triage_dir(logdir: Path) -> Report:
    report = Report()
    for name in LOG_FILES:
        path = logdir / name
        if not path.is_file():
            report.missing_logs.append(name)
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        report.lines_read[name] = len(lines)
        triage_lines(name, lines, report)
    return report


def render(report: Report, logdir: Path) -> str:
    out = ["# Log triage", "", f"Log folder: `{logdir}`", ""]
    if report.lines_read:
        read = ", ".join(f"{name} ({count} lines)" for name, count in report.lines_read.items())
        out.append(f"Read: {read}")
    if report.missing_logs:
        out.append(f"Missing: {', '.join(report.missing_logs)}")
    out.append("")

    issues = list(report.issues.values())
    errors = sum(i.count for i in issues if i.severity == "error")
    warnings = sum(i.count for i in issues if i.severity == "warning")
    out.append(f"**{errors} error lines, {warnings} warning lines, {len(issues)} unique.**")
    out.append("")

    if not issues:
        out.append("No errors or warnings found.")
        return "\n".join(out) + "\n"

    out.append("## Summary by source")
    out.append("")
    out.append("| Source | Errors | Warnings |")
    out.append("|---|---|---|")
    grouped = report.by_source()
    for source, items in grouped.items():
        e = sum(i.count for i in items if i.severity == "error")
        w = sum(i.count for i in items if i.severity == "warning")
        out.append(f"| {source} | {e} | {w} |")
    out.append("")

    for source, items in grouped.items():
        out.append(f"## {source}")
        out.append("")
        for issue in items:
            times = f" (x{issue.count})" if issue.count > 1 else ""
            out.append(f"- **{issue.log}:{issue.first_line}** [{issue.severity}]{times} `{issue.message}`")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("logdir", type=Path, help="folder holding the Civ 6 log files")
    parser.add_argument("--out", type=Path, help="write the report here instead of printing it")
    args = parser.parse_args(argv)

    if not args.logdir.is_dir():
        print(f"error: {args.logdir} is not a folder", file=sys.stderr)
        return 2

    report = triage_dir(args.logdir)
    if len(report.missing_logs) == len(LOG_FILES):
        print(f"error: none of {', '.join(LOG_FILES)} found in {args.logdir}", file=sys.stderr)
        return 2

    text = render(report, args.logdir)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
