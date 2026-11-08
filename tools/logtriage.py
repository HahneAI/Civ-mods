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

# How far back and ahead to look for a file path when the error line has none.
# Database.log names the file a few lines AFTER the error, so look both ways.
CONTEXT_BEFORE = 3
CONTEXT_AFTER = 4

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
# Firaxis files and messages that show up with no mods at all. Seen in the
# owner's first real logs (docs/playtests/001-ui-group.md).
GAME_NOISE = re.compile(
    r"CurrentClickouts/|HallOfFame/|_Gossip_Text\.xml|_Translations_ConfigText_"
    r"|Service missing\. Skipping|LocalizedText - Failed loading XML",
    re.I,
)

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
        order = lambda i: (i.source == UNKNOWN, i.source == BASE, i.source.lower())
        for issue in sorted(self.issues.values(), key=order):
            grouped.setdefault(issue.source, []).append(issue)
        return grouped


def strip_timestamp(line: str) -> str:
    return TIMESTAMP.sub("", line).strip()


def find_source(text: str) -> str | None:
    match = MOD_PATH.search(text)
    if match:
        return match.group(1).strip()
    if GAME_PATH.search(text) or GAME_NOISE.search(text):
        return BASE
    return None


def is_issue(log: str, line: str) -> bool:
    if IGNORE_PATTERNS.search(line):
        return False
    return bool(ERROR_PATTERNS[log].search(line))


def nearby_source(log: str, lines: list[str], i: int) -> str | None:
    before = [lines[j] for j in range(i - 1, max(-1, i - 1 - CONTEXT_BEFORE), -1)]
    after = lines[i + 1 : i + 1 + CONTEXT_AFTER]
    # Database.log puts the file after the error; other logs put it before.
    order = after + before if log == "Database.log" else before + after
    for text in order:
        source = find_source(text)
        if source:
            return source
    return None


def triage_lines(log: str, lines: list[str], report: Report) -> None:
    cleaned = [strip_timestamp(raw) for raw in lines]
    last_source: str | None = None
    for i, line in enumerate(cleaned):
        if not line:
            continue
        here = find_source(line)
        if is_issue(log, line):
            source = here or nearby_source(log, cleaned, i)
            if source is None and log == "Modding.log":
                # Modding.log names the component being applied before it fails.
                source = last_source
            severity = "warning" if WARNING_WORDS.search(line) else "error"
            report.add(Issue(log, severity, line, source or UNKNOWN, first_line=i + 1))
        if here:
            last_source = here


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
        if source == BASE:
            out.append("_Firaxis files. These also appear with no mods enabled, so they are usually harmless._")
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
