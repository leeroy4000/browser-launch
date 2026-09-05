# CLAUDE.md

`README.md` is thorough and user-facing (features, config format,
troubleshooting) — read it first. This adds source-level orientation.

## Note: repo name vs. folder name

GitHub repo is `leeroy4000/browser-launch` — this local directory is named
`browser-launcher`. Not a typo to fix, just don't be surprised when `git
remote -v` shows a different name than the folder.

## Code structure

Single file, `browser-launch.py` (~38KB, function-based). Rough layout:

- `check_and_install_dependencies`, `detect_browsers` — startup
  environment probing (auto-installs `pyyaml`/`requests` if missing,
  detects which of Brave/Firefox/Chrome/Chromium/Edge is present).
- `setup_logging`, `load_config` — config lives at
  `~/Documents/Configs/browser-launch.yaml` on both platforms (same
  relative path on Windows via `%USERPROFILE%`).
- `run_setup_wizard`, `add_captive_portal` — interactive `--setup`/
  `--add-portal` flows.
- `install_autostart`/`_install_windows_task`/`_install_systemd_service`,
  `uninstall_autostart` — platform-specific autostart registration
  (systemd user service on Linux, Task Scheduler on Windows).
- `has_internet_connection`, `wait_for_internet`, `_get_current_ssid`,
  `is_service_reachable` — network/health-check primitives. SSID
  detection is `nmcli` (Linux) / `netsh` (Windows) — captive-portal
  matching depends on this working correctly on whatever network you're on.
- `launch_and_accept` — Playwright-driven captive-portal auto-accept, using
  the button CSS selector from config.
- `clear_brave_session_restore`, `_get_brave_profile_dir` — the "clean
  boot" feature: kills Brave, deletes session files, patches Preferences to
  mark exit as clean, so a reboot-without-closing doesn't restore stale
  tabs. Brave-specific; other browsers aren't session-cleaned.
- `open_tabs` — the actual per-window tab launcher, gated by health checks.
- `main`/`_run` — CLI entry point, argument dispatch (`--run`/`--setup`/
  `--add-portal`/`--install`/`--uninstall`), PID-lockfile guard against
  double-launch from autostart firing twice.

## Working on this

- Cross-platform by design (Linux + Windows from one file) — any change to
  paths, process management, or autostart must be checked against both
  platform branches, not just the one you're testing on.
- No test suite. Changes to `clear_brave_session_restore` or
  `launch_and_accept` are the riskiest to verify blind — they touch a real
  browser's live profile/session state, so test by actually running
  `--run`, not just reading the diff.
