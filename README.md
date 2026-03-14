# 🧹 Inbound Maiden

**Keeps your OpenClaw media inbound folder from quietly filling up.**

Your agent reads voice messages, images, and files from an inbound folder. Great. What nobody told you is that folder never empties itself. A few weeks in you've got hundreds of processed files sitting there doing nothing, and at some point you'll notice the disk and wonder where it all went.

inbound-maiden fixes that. Anything old enough gets moved to an archive. Anything in the archive that's been there long enough gets deleted. You configure the thresholds once at setup, cron handles the rest, and your inbound folder stays clean without you thinking about it.

---

## How it works

```
cron fires twice daily
  → inbound-maiden scans ~/.openclaw/media/inbound/
  → files older than N days → moved to ~/.openclaw/media/archive/
  → files in archive older than M days → deleted
  → report written to ~/.openclaw/logs/inbound-maiden.log
```

No daemon. No database. No watch process. Just cron, Python, and a config file.

---

## What it touches

| Path | What happens |
|------|-------------|
| `~/.openclaw/media/inbound/` | Source — aged files moved out |
| `~/.openclaw/media/archive/` | Holding area — files pruned after retention period |
| `~/.openclaw/logs/inbound-maiden.log` | Cron output |

Everything else on your system is untouched.

---

## Requirements

- Python 3.6+ — stdlib only, no pip installs

No sudo. No root. No system-level writes outside `~/.openclaw/`.

---

## Install

```bash
cp -r inbound-maiden/ ~/.openclaw/skills/inbound-maiden/
python3 ~/.openclaw/skills/inbound-maiden/setup.py
```

The setup script creates the inbound and archive directories if they don't exist, asks for your age threshold and retention period in days, sets the cron schedule, and installs the cron entries — all interactive, nothing silent.

---

## Usage

```bash
python3 ~/.openclaw/skills/inbound-maiden/inbound_maiden.py <command>
```

### Commands

| Command | What it does |
|---------|-------------|
| `run` | Archive aged files, prune old archives, print report |
| `run --dry-run` | Show what would happen without touching anything |
| `status` | File counts and sizes for inbound and archive |

### Examples

```bash
# Check the current state
python3 inbound_maiden.py status

# Preview a cleanup run
python3 inbound_maiden.py run --dry-run

# Run manually
python3 inbound_maiden.py run
```

---

## Output

```
[inbound-maiden] Cleanup — 2026-03-11 06:00
  min age: 3d · retain: 30d

  Archived (3):
    → voice_20260307_143201.ogg  (3.8d old)
    → photo_20260306_091442.jpg  (4.9d old)
    → doc_20260305_172310.pdf    (5.5d old)

  Pruned from archive (1):
    ✕ voice_20260209_081100.ogg  (modified 2026-02-09)

  Skipped — too recent (2):
    · voice_20260310_112233.ogg  (0.8d old)
    · photo_20260311_074512.jpg  (0.1d old)
```

---

## Configuration

Config lives at `~/.openclaw/config/inbound-maiden/maiden.json`:

```json
{
  "min_age_days": 3,
  "retain_days": 30
}
```

Edit directly to adjust thresholds. Values are read fresh on every run — no restart needed.

---

## Files

| File | Purpose |
|------|---------|
| `inbound_maiden.py` | Everything. One script. |
| `setup.py` | Interactive first-run configurator |

That's it. Two scripts.

---

## Release checksums (v1.0.0)

```
1ac0580d73ef3f239e0ac08995e9f37cabdbb99376c442a12399a5b31ac3b848  inbound_maiden.py
c0a1618753ba70457614502cb5bcebbaf7cd5ff8d52ff75a8d415234833b2048  setup.py
```

```bash
sha256sum inbound_maiden.py setup.py
```

---

## Part of the hiVe stack

inbound-maiden was built as part of [hiVe](https://github.com/LittleJakub) — a personal multi-agent system running on OpenClaw. It's the simplest possible answer to a folder that never empties itself.

If you're running your own OpenClaw setup and your inbound folder is quietly growing, this is for you.

---

## License

MIT. Do whatever you want with it. If it saves your bacon, a ⭐ is always appreciated.
