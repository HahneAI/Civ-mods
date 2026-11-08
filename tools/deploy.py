"""Copy mod/CivLayer into the game's Mods folder.

The target folder is chosen in this order:
    1. --mods-dir
    2. the CIVLAYER_MODS_DIR environment variable
    3. the Windows default: Documents/My Games/Sid Meier's Civilization VI/Mods

On other systems, or if Documents is moved (e.g. OneDrive), pass --mods-dir.

Safety: an existing Mods/CivLayer folder is replaced only if it holds a
CivLayer.modinfo, so a wrong path can't wipe an unrelated folder.

Usage:
    python tools/deploy.py [--mods-dir PATH] [--dry-run]

Source: custom (SPEC section 5, tools table).
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

MOD_NAME = "CivLayer"
MODINFO = f"{MOD_NAME}.modinfo"
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "mod" / MOD_NAME
ENV_VAR = "CIVLAYER_MODS_DIR"

# Editor, OS and git leftovers that should never reach the game folder.
SKIP_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", "__pycache__", ".git"}
SKIP_SUFFIXES = (".bak", ".tmp", ".swp", "~")


class DeployError(Exception):
    pass


def windows_default() -> Path:
    return Path.home() / "Documents" / "My Games" / "Sid Meier's Civilization VI" / "Mods"


def resolve_mods_dir(cli_value: Path | None, env: dict[str, str] | None = None) -> Path:
    env = os.environ if env is None else env
    if cli_value:
        return cli_value
    if env.get(ENV_VAR):
        return Path(env[ENV_VAR])
    if sys.platform == "win32":
        return windows_default()
    raise DeployError(
        f"no Mods folder given. Pass --mods-dir or set {ENV_VAR} "
        "(the default path is only known for Windows)."
    )


def ignore(_dir: str, names: list[str]) -> set[str]:
    return {n for n in names if n in SKIP_NAMES or n.endswith(SKIP_SUFFIXES)}


def list_files(source: Path) -> list[Path]:
    files = []
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if any(part in SKIP_NAMES for part in rel.parts) or path.name.endswith(SKIP_SUFFIXES):
            continue
        if path.is_file():
            files.append(rel)
    return files


def check_source(source: Path) -> None:
    if not source.is_dir():
        raise DeployError(f"{source} does not exist. The mod folder is created in TODO Phase 3.")
    if not (source / MODINFO).is_file():
        raise DeployError(f"{source} has no {MODINFO}. The game won't load it.")


def check_target(mods_dir: Path, target: Path) -> None:
    if not mods_dir.is_dir():
        raise DeployError(
            f"Mods folder {mods_dir} does not exist. Check the path "
            "(start Civ 6 once, or create the folder yourself)."
        )
    if target.exists() and not (target / MODINFO).is_file():
        raise DeployError(
            f"{target} exists but holds no {MODINFO}. Refusing to replace it. "
            "Move or delete it by hand if it's safe."
        )


def deploy(source: Path, mods_dir: Path, dry_run: bool = False) -> list[Path]:
    """Copy source into mods_dir/CivLayer. Returns the files copied (relative paths)."""
    check_source(source)
    target = mods_dir / MOD_NAME
    check_target(mods_dir, target)
    files = list_files(source)
    if dry_run:
        return files
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=ignore)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mods-dir", type=Path, help="the game's Mods folder")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help="list what would be copied, change nothing")
    args = parser.parse_args(argv)

    try:
        mods_dir = resolve_mods_dir(args.mods_dir)
        files = deploy(args.source, mods_dir, dry_run=args.dry_run)
    except DeployError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    target = mods_dir / MOD_NAME
    verb = "would copy" if args.dry_run else "copied"
    print(f"{verb} {len(files)} files to {target}")
    if args.dry_run:
        for rel in files:
            print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
