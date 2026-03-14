# inbound-maiden

**What this skill is**: Scheduled cleanup for `~/.openclaw/media/inbound/`. Moves files that have been sitting untouched for long enough to an archive folder, then prunes the archive after a configurable retention period.

**What this skill is NOT**: A transcriber, a processor, or a decision-maker. It doesn't know what's in a file — it only knows how old it is. Processing voice messages and acting on their content is your job. inbound-maiden just keeps the folder from filling up.

---

## When to use it

You don't need to call this skill manually. It runs on cron twice a day. It will never touch a file that arrived recently — only files older than the configured minimum age get moved.

If Jakub asks about the inbound folder state, use `status`. If he asks you to run a cleanup manually, use `run`. If he wants to check what *would* happen without actually moving anything, use `run --dry-run`.

---

## Script location

```
~/.openclaw/agents/main/workspace/skills/inbound-maiden/inbound_maiden.py
```

---

## Commands

### run — Archive aged files and prune old archives

```bash
python3 inbound_maiden.py run
```

- Moves any file in `inbound/` older than `min_age_days` → `archive/`
- Deletes any file in `archive/` older than `retain_days`
- Prints a clear report of everything moved and pruned

```bash
# Preview without touching anything
python3 inbound_maiden.py run --dry-run
```

---

### status — Check folder state

```bash
python3 inbound_maiden.py status
```

Output example:
```
[inbound-maiden] Status
  config:   min_age=3d · retain=30d
  inbound:  12 files · 48.3 MB  (3 ready to archive)
  archive:  47 files · 182.1 MB
```

---

## Paths

| Path | Purpose |
|------|---------|
| `~/.openclaw/media/inbound/` | Drop zone — rOe reads from here |
| `~/.openclaw/media/archive/` | Holding area — files kept for `retain_days` then deleted |
| `~/.openclaw/config/inbound-maiden/maiden.json` | Config — `min_age_days`, `retain_days` |
| `~/.openclaw/logs/inbound-maiden.log` | Cron output log |

---

## Config

```json
{
  "min_age_days": 3,
  "retain_days": 30
}
```

Edit `maiden.json` directly to change thresholds. No restart needed — values are read fresh on every run.
