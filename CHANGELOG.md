# inbound-maiden Changelog

## [1.0.0] — 2026-03-14

Initial release.

### Added
- `run` — archive files from inbound older than `min_age_days`, prune archive files older than `retain_days`
- `run --dry-run` — preview what would be moved/deleted without touching anything
- `status` — file counts and sizes for inbound and archive directories
- Collision-safe archiving — appends timestamp to filename if destination already exists
- `setup.py` — interactive configurator: creates dirs, writes config, installs cron entries
- Config at `~/.openclaw/config/inbound-maiden/maiden.json`
- Pure stdlib Python — no pip dependencies
