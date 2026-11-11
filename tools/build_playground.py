"""Build docs/schema/playground.html from its parts.

The playground is one self-contained page: the template, the JavaScript checker, the closed
lists, the four variables, and the example dataset are inlined, so it opens by double-click
and publishes as a single artifact. Edit the parts, then run this script.

Usage:
    python tools/build_playground.py            # writes docs/schema/playground.html
    python tools/build_playground.py --fragment OUT.html   # also write the body-only version

Source: custom (docs/schema).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCHEMA = Path(__file__).resolve().parent.parent / "docs" / "schema"


def _json(path: Path) -> str:
    # compact; "</" is escaped so the data can never close the script tag
    return json.dumps(json.loads(path.read_text(encoding="utf-8")), separators=(",", ":")).replace("</", "<\\/")


def fragment() -> str:
    tpl = (SCHEMA / "playground.template.html").read_text(encoding="utf-8")
    js = (SCHEMA / "playground-check.js").read_text(encoding="utf-8")
    sim = (SCHEMA / "playground-sim.js").read_text(encoding="utf-8")
    out = tpl.replace("/*@CHECKJS@*/", js.replace("</script", "<\\/script"))
    out = out.replace("/*@SIMJS@*/", sim.replace("</script", "<\\/script"))
    out = out.replace("/*@ENUMS@*/null", _json(SCHEMA / "enums.json"))
    out = out.replace("/*@VARIANTS@*/null", _json(SCHEMA / "variants.json"))
    out = out.replace("/*@EXAMPLE@*/null", _json(SCHEMA / "example-data.json"))
    return out


def standalone() -> str:
    """The fragment wrapped in a document skeleton, for opening the file directly."""
    body = fragment()
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            "</head>\n<body>\n" + body + "\n</body>\n</html>\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fragment", help="also write the body-only version here (for publishing as an artifact)")
    args = ap.parse_args(argv)
    (SCHEMA / "playground.html").write_text(standalone(), encoding="utf-8")
    print("Wrote docs/schema/playground.html")
    if args.fragment:
        Path(args.fragment).write_text(fragment(), encoding="utf-8")
        print(f"Wrote {args.fragment}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
