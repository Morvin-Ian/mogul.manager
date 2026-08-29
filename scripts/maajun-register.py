#!/usr/bin/env python3
"""Register a repo with maajun, including its deployment block.

`maajun add-repo` creates a bare entry — repo, base_branch, mode — with no
[github.repos.deployment] section. Without that section maajun has no idea
where the app runs, which containers belong to it, or where its logs are, so
it can only react to what is visible on GitHub. This script fills that gap.

It is idempotent: re-running against an existing repo updates only the fields
you pass and leaves the rest alone, so it doubles as an edit tool.

Usage
-----
    ./maajun-register.py --repo OWNER/NAME --path /srv/app --port 8080 \
        --container app-web --container app-api

    ./maajun-register.py --repo OWNER/NAME --mode fix --dry-run

Every write is preceded by a timestamped backup, and the generated TOML is
re-parsed and compared field-by-field against the intended structure before it
replaces the original. If that comparison fails, nothing is written.

Note: the config is rewritten from its parsed form, so comments and manual
formatting in the original file are not preserved. The backup keeps them.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import sys
import time
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        sys.exit(
            "error: need Python 3.11+ (for tomllib) or `pip install tomli`.\n"
            f"       running {sys.version.split()[0]}"
        )

# Ordered by how likely they are, most specific first.
CONFIG_CANDIDATES = [
    "~/.config/maajun/config.toml",
    "~/.maajun/config.toml",
    "~/.maajun.toml",
    "/etc/maajun/config.toml",
    "./maajun.toml",
]


# ── TOML output ──────────────────────────────────────────────────────


def _is_table(v: object) -> bool:
    return isinstance(v, dict)


def _is_array_of_tables(v: object) -> bool:
    return isinstance(v, list) and len(v) > 0 and all(isinstance(i, dict) for i in v)


def _fmt(v: object) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        # TOML basic strings share JSON's escape syntax.
        return json.dumps(v)
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, list):
        return "[" + ", ".join(_fmt(i) for i in v) + "]"
    raise TypeError(f"cannot serialise {type(v).__name__} to TOML: {v!r}")


def _dump(table: dict, prefix: str, out: list[str]) -> None:
    """Emit one table. Scalars must precede sub-tables to stay valid TOML."""
    for k, v in table.items():
        if not _is_table(v) and not _is_array_of_tables(v):
            out.append(f"{k} = {_fmt(v)}")

    for k, v in table.items():
        name = f"{prefix}.{k}" if prefix else k
        if _is_table(v):
            # A table holding nothing but sub-tables needs no header of its
            # own — [github] above [[github.repos]] is just noise. An actually
            # empty table does need one, or it would vanish.
            has_scalars = any(
                not _is_table(x) and not _is_array_of_tables(x) for x in v.values()
            )
            if has_scalars or not v:
                out.append("")
                out.append(f"[{name}]")
            _dump(v, name, out)
        elif _is_array_of_tables(v):
            for item in v:
                out.append("")
                out.append(f"[[{name}]]")
                _dump(item, name, out)


def dumps(doc: dict) -> str:
    out: list[str] = []
    _dump(doc, "", out)
    # Collapse the leading blank line produced by the first table header.
    text = "\n".join(out).lstrip("\n")
    return text + "\n"


# ── config location ──────────────────────────────────────────────────


def find_config(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser()
        if not p.is_file():
            sys.exit(f"error: no config at {p}")
        return p

    for cand in CONFIG_CANDIDATES:
        p = Path(cand).expanduser()
        if p.is_file():
            return p

    sys.exit(
        "error: could not find maajun's config. Looked in:\n"
        + "".join(f"  {Path(c).expanduser()}\n" for c in CONFIG_CANDIDATES)
        + "Pass it explicitly with --config /path/to/config.toml"
    )


# ── the edit ─────────────────────────────────────────────────────────


def build_updates(args: argparse.Namespace) -> tuple[dict, dict]:
    """Split the CLI args into repo-level and deployment-level fields.

    Only fields the caller actually passed appear, so an update never clobbers
    a value it was not asked to change.
    """
    repo_fields: dict = {}
    if args.base_branch is not None:
        repo_fields["base_branch"] = args.base_branch
    if args.mode is not None:
        repo_fields["mode"] = args.mode
    if args.test_command is not None:
        repo_fields["test_command"] = args.test_command

    dep_fields: dict = {}
    if args.path is not None:
        dep_fields["path"] = args.path
    if args.runs is not None:
        dep_fields["runs"] = args.runs
    if args.stack is not None:
        dep_fields["stack"] = args.stack
    if args.port is not None:
        dep_fields["port"] = args.port
    if args.log_file is not None:
        dep_fields["log_files"] = args.log_file
    if args.container is not None:
        dep_fields["docker_containers"] = args.container

    return repo_fields, dep_fields


def apply(doc: dict, repo: str, repo_fields: dict, dep_fields: dict) -> str:
    github = doc.setdefault("github", {})
    repos = github.setdefault("repos", [])
    if not isinstance(repos, list):
        sys.exit("error: [github].repos is not an array of tables — refusing to edit")

    entry = next((r for r in repos if r.get("repo") == repo), None)
    action = "updated"
    if entry is None:
        entry = {"repo": repo}
        repos.append(entry)
        action = "added"

    entry.update(repo_fields)

    if dep_fields:
        deployment = entry.setdefault("deployment", {})
        deployment.update(dep_fields)
        # Keep `deployment` last so the entry reads like the existing ones.
        entry["deployment"] = entry.pop("deployment")

    return action


def verify(text: str, expected: dict) -> None:
    """Re-parse the generated TOML and require it to match exactly."""
    try:
        got = tomllib.loads(text)
    except Exception as exc:
        sys.exit(f"error: generated TOML does not parse ({exc}) — nothing written")
    if got != expected:
        sys.exit(
            "error: generated TOML does not round-trip to the intended config — "
            "nothing written. This is a bug in this script; your config is untouched."
        )


# ── main ─────────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Register a repo with maajun, including its deployment block.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--repo", required=True, help="OWNER/NAME, must match exactly")
    ap.add_argument("--config", help="path to maajun's config.toml (auto-detected)")

    ap.add_argument("--base-branch", help="e.g. main, master")
    ap.add_argument("--mode", choices=["suggest", "fix"], help="suggest or fix")
    ap.add_argument("--test-command", help="gate for fix mode, e.g. 'make test'")

    ap.add_argument("--path", help="deployment directory on this host")
    ap.add_argument("--runs", help="how it starts, e.g. 'docker compose -f ...'")
    ap.add_argument("--stack", help="one-line description of the runtime")
    ap.add_argument("--port", type=int, help="port to health-check")
    ap.add_argument(
        "--container",
        action="append",
        metavar="NAME",
        help="container belonging to this app (repeat per container)",
    )
    ap.add_argument(
        "--log-file",
        action="append",
        metavar="PATH",
        help="on-disk log file (repeat). Omit for stdout-only apps.",
    )

    ap.add_argument("--dry-run", action="store_true", help="print the diff, write nothing")
    args = ap.parse_args()

    repo_fields, dep_fields = build_updates(args)
    if not repo_fields and not dep_fields:
        sys.exit("error: nothing to do — pass at least one field to set")

    config_path = find_config(args.config)
    original = config_path.read_text()
    try:
        doc = tomllib.loads(original)
    except Exception as exc:
        sys.exit(f"error: {config_path} is not valid TOML ({exc})")

    action = apply(doc, args.repo, repo_fields, dep_fields)
    new_text = dumps(doc)
    verify(new_text, doc)

    diff = list(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile=str(config_path),
            tofile=f"{config_path} (new)",
        )
    )
    if not diff:
        print(f"no change — {args.repo} already configured as requested")
        return

    sys.stdout.writelines(diff)

    if args.dry_run:
        print(f"\n[dry-run] would have {action} {args.repo}; nothing written")
        return

    backup = config_path.with_suffix(config_path.suffix + f".bak.{int(time.time())}")
    shutil.copy2(config_path, backup)

    # Write to a sibling temp file and rename, so an interrupted run cannot
    # leave a half-written config behind.
    tmp = config_path.with_suffix(config_path.suffix + ".tmp")
    tmp.write_text(new_text)
    os.replace(tmp, config_path)

    print(f"\n{action} {args.repo}")
    print(f"backup: {backup}")
    print("run `maajun config` to confirm, and restart the daemon to pick it up")


if __name__ == "__main__":
    main()
