#!/usr/bin/env python3
"""
inbound-maiden setup — interactive first-run configurator
"""

import json
import os
import subprocess
import sys

CONFIG_DIR  = os.path.expanduser("~/.openclaw/config/inbound-maiden/")
CONFIG_PATH = os.path.join(CONFIG_DIR, "maiden.json")
INBOUND_DIR = os.path.expanduser("~/.openclaw/media/inbound/")
ARCHIVE_DIR = os.path.expanduser("~/.openclaw/media/archive/")
SKILL_DIR   = os.path.dirname(os.path.abspath(__file__))


def check(label: str, cmd: list) -> bool:
    try:
        ok = subprocess.run(cmd, capture_output=True).returncode == 0
    except FileNotFoundError:
        ok = False
    print(f"  [{'✓' if ok else '✗'}] {label}")
    return ok


def ask_int(prompt: str, default: int, min_val: int = 1) -> int:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        try:
            val = int(raw)
            if val >= min_val:
                return val
            print(f"  Must be at least {min_val}.")
        except ValueError:
            print("  Please enter a whole number.")


def ask_cron(hour_morning: int, hour_evening: int) -> list[str]:
    script = os.path.join(SKILL_DIR, "inbound_maiden.py")
    log    = os.path.expanduser("~/.openclaw/logs/inbound-maiden.log")
    cmd    = f"python3 {script} run >> {log} 2>&1"
    return [
        f"0 {hour_morning} * * * {cmd}",
        f"0 {hour_evening} * * * {cmd}",
    ]


def install_cron(lines: list[str]) -> None:
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    cleaned = "\n".join(
        l for l in existing.splitlines()
        if "inbound_maiden" not in l and "inbound-maiden" not in l
    )
    new_crontab = cleaned.rstrip("\n") + "\n" + "\n".join(lines) + "\n"

    proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True)
    if proc.returncode != 0:
        print("  [!] crontab write failed — add the lines manually.")
    else:
        print("  [✓] Crontab updated.")


def main():
    print("=" * 52)
    print("  inbound-maiden setup")
    print("=" * 52)

    # Deps
    print("\nChecking dependencies:")
    py_ok = check("python3", ["python3", "--version"])
    if not py_ok:
        sys.exit("\n[setup] python3 is required.")

    # Dirs
    print("\nCreating directories:")
    for path in [INBOUND_DIR, ARCHIVE_DIR, CONFIG_DIR]:
        existed = os.path.exists(path)
        os.makedirs(path, exist_ok=True)
        status = "Already exists" if existed else "Created"
        print(f"  [✓] {status}: {path}")

    # Config questions
    print("\nConfiguration:")
    print("  How many days must a file sit in inbound before it's archived?")
    min_age_days = ask_int("  Min age in days", default=3)

    print("\n  How many days should files stay in the archive before being deleted?")
    retain_days = ask_int("  Retain days", default=30)

    # Cron schedule
    print("\nCron schedule:")
    print("  inbound-maiden will run twice daily.")
    hour_morning = ask_int("  Morning run hour (0–23)", default=6, min_val=0)
    hour_evening = ask_int("  Evening run hour (0–23)", default=18, min_val=0)
    cron_lines = ask_cron(hour_morning, hour_evening)

    # Write config
    config = {
        "min_age_days": min_age_days,
        "retain_days": retain_days,
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\n  [✓] Config written: {CONFIG_PATH}")

    # Mark script executable
    script = os.path.join(SKILL_DIR, "inbound_maiden.py")
    if os.path.exists(script):
        os.chmod(script, 0o755)
        print(f"  [✓] inbound_maiden.py marked executable")

    # Cron
    print(f"\nProposed crontab entries:")
    for line in cron_lines:
        print(f"  {line}")
    answer = input("\nInstall these cron entries? [Y/n]: ").strip().lower()
    if answer in ("", "y", "yes"):
        install_cron(cron_lines)
    else:
        print("  Skipped — add them manually if needed.")

    print("\n" + "=" * 52)
    print("  Setup complete.")
    print("=" * 52)
    print(f"\nDry run to verify:")
    print(f"  python3 {script} run --dry-run")
    print(f"\nCheck status anytime:")
    print(f"  python3 {script} status")
    print()


if __name__ == "__main__":
    main()
