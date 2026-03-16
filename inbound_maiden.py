#!/usr/bin/env python3
"""
inbound-maiden — periodic cleanup of ~/.openclaw/media/inbound/
Moves aged files to archive, prunes archive after retention period.
"""

import json
import os
import sys
import shutil
import argparse
from datetime import datetime, timedelta
OC          = os.environ.get("OPENCLAW_STATE_DIR", os.path.expanduser("~/.openclaw"))
CONFIG_PATH = os.path.join(OC, "config/inbound-maiden/maiden.json")
INBOUND_DIR = os.path.join(OC, "media/inbound/")
ARCHIVE_DIR = os.path.join(OC, "media/archive/")


# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        sys.exit(
            f"[inbound-maiden] Config not found at {CONFIG_PATH}. Run setup.py first."
        )
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


# ── Core logic ────────────────────────────────────────────────────────────────

def file_age_days(path: str) -> float:
    mtime = os.path.getmtime(path)
    age = datetime.now() - datetime.fromtimestamp(mtime)
    return age.total_seconds() / 86400


def run_cleanup(dry_run: bool = False) -> None:
    config = load_config()
    min_age_days: float = config["min_age_days"]
    retain_days: int = config["retain_days"]

    now = datetime.now()
    label = "[DRY RUN] " if dry_run else ""

    archived = []
    skipped = []
    pruned = []
    errors = []

    # ── Step 1: archive aged files from inbound ───────────────────────────────
    if not os.path.exists(INBOUND_DIR):
        print(f"[inbound-maiden] Inbound dir not found: {INBOUND_DIR}")
        return

    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    for fname in sorted(os.listdir(INBOUND_DIR)):
        fpath = os.path.join(INBOUND_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        age_d = file_age_days(fpath)
        if age_d < min_age_days:
            skipped.append((fname, age_d))
            continue

        dest = os.path.join(ARCHIVE_DIR, fname)

        # Avoid collisions — append timestamp if name already exists in archive
        if os.path.exists(dest):
            stem, ext = os.path.splitext(fname)
            ts = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y%m%d%H%M%S")
            dest = os.path.join(ARCHIVE_DIR, f"{stem}_{ts}{ext}")

        try:
            if not dry_run:
                shutil.move(fpath, dest)
            archived.append((fname, age_d))
        except Exception as e:
            errors.append((fname, str(e)))

    # ── Step 2: prune old files from archive ──────────────────────────────────
    cutoff = now - timedelta(days=retain_days)

    for fname in sorted(os.listdir(ARCHIVE_DIR)):
        fpath = os.path.join(ARCHIVE_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
        if mtime < cutoff:
            try:
                if not dry_run:
                    os.remove(fpath)
                pruned.append((fname, mtime.strftime("%Y-%m-%d")))
            except Exception as e:
                errors.append((fname, str(e)))

    # ── Report ────────────────────────────────────────────────────────────────
    print(f"[inbound-maiden] {label}Cleanup — {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"  min age: {min_age_days}d · retain: {retain_days}d")
    print()

    if archived:
        print(f"  Archived ({len(archived)}):")
        for fname, age_d in archived:
            print(f"    → {fname}  ({age_d:.1f}d old)")
    else:
        print("  Archived: nothing to move")

    if skipped:
        print(f"  Skipped — too recent ({len(skipped)}):")
        for fname, age_d in skipped:
            print(f"    · {fname}  ({age_d:.1f}d old)")

    if pruned:
        print(f"  Pruned from archive ({len(pruned)}):")
        for fname, date_str in pruned:
            print(f"    ✕ {fname}  (modified {date_str})")
    else:
        print("  Pruned: nothing expired")

    if errors:
        print(f"  Errors ({len(errors)}):")
        for fname, msg in errors:
            print(f"    ! {fname}: {msg}")
        sys.exit(1)


def run_status() -> None:
    config = load_config()
    min_age_days = config["min_age_days"]
    retain_days = config["retain_days"]

    def dir_summary(path: str) -> tuple[int, int]:
        if not os.path.exists(path):
            return 0, 0
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        total = sum(os.path.getsize(os.path.join(path, f)) for f in files)
        return len(files), total

    def fmt_size(b: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"

    in_count, in_size = dir_summary(INBOUND_DIR)
    ar_count, ar_size = dir_summary(ARCHIVE_DIR)

    ready = 0
    if os.path.exists(INBOUND_DIR):
        for fname in os.listdir(INBOUND_DIR):
            fpath = os.path.join(INBOUND_DIR, fname)
            if os.path.isfile(fpath) and file_age_days(fpath) >= min_age_days:
                ready += 1

    print("[inbound-maiden] Status")
    print(f"  config:   min_age={min_age_days}d · retain={retain_days}d")
    print(f"  inbound:  {in_count} files · {fmt_size(in_size)}"
          + (f"  ({ready} ready to archive)" if ready else ""))
    print(f"  archive:  {ar_count} files · {fmt_size(ar_size)}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="inbound_maiden.py",
        description="inbound-maiden — cleans up ~/.openclaw/media/inbound/ on a schedule",
    )
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    p = sub.add_parser("run", help="Run cleanup (archive aged files, prune old archives)")
    p.add_argument("--dry-run", action="store_true", help="Show what would happen without moving anything")
    p.set_defaults(func=lambda a: run_cleanup(dry_run=a.dry_run))

    p = sub.add_parser("status", help="Show inbound and archive file counts")
    p.set_defaults(func=lambda a: run_status())

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
