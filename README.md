# Browser Launch

Launch your browser with a clean, organized set of windows and tabs every time you log in. Configurable via YAML, with health checks for local services, captive portal auto-accept, and cross-platform support (Linux & Windows). Includes Brave-specific session cleanup so reboots never leave stale windows behind. Supports Brave, Chrome, Firefox, Chromium, and Edge.

## Features

- 🚀 **Auto-launch at login** - Opens your browser with organized tabs automatically
- 🏥 **Health checks** - Skip tabs for services that are down
- 📶 **Captive portal support** - Auto-accept WiFi login pages
- 🔧 **Interactive setup** - Easy configuration wizard
- 🌐 **Multi-browser support** - Brave, Firefox, Chrome, Chromium, Edge
- 🖥️ **Cross-platform** - Works on Linux and Windows with a single config file
- 📝 **YAML configuration** - Simple file editing for tab management
- 🧹 **Clean boot** - Clears previous Brave sessions so you get a fresh environment every login
- ⚙️ **Autostart integration** - systemd on Linux, Task Scheduler on Windows

## Quick Start

### Linux

```bash
git clone https://github.com/leeroy4000/browser-launch.git
cd browser-launch
chmod +x browser-launch.py
./browser-launch.py
```

### Windows

```powershell
git clone https://github.com/leeroy4000/browser-launch.git
cd browser-launch
python browser-launch.py
```

The setup wizard will:
- Detect installed browsers
- Configure captive portal (if needed)
- Set up your tabs and windows
- Install autostart (optional) — systemd service on Linux, Task Scheduler task on Windows

Your browser will launch automatically at next login with your configured tabs.

## Configuration

The configuration file is stored at `~/Documents/Configs/browser-launch.yaml` on both platforms.

On Windows, this resolves to `C:\Users\<you>\Documents\Configs\browser-launch.yaml`.

### Example Configuration

```yaml
# Captive portal settings (optional)
captive_portals: []
  # - ssid: "Guest WiFi"
  #   url: "https://login.example.com/"
  #   accept_button_selector: 'input[value="Accept"]'
  #   max_retries: 3
  #   retry_delay: 2

# Browser windows
windows:
  # Network monitoring and infrastructure
  Network:
    delay: 2
    health_check: true
    tabs:
      - name: Home Assistant
        url: http://192.168.1.9:8123/dashboard-default/0

      - name: Proxmox
        url: 'https://192.168.1.8:8006/#v1:0:18:4:::::::'

  # AI tools and productivity
  AI:
    delay: 5
    health_check: true
    tabs:
      - name: Claude
        url: https://claude.ai/

      - name: Github Copilot
        url: https://github.com/copilot

# General settings
settings:
  wait_before_start: 15        # Seconds to wait for desktop environment
  health_check_timeout: 3      # Seconds to wait for each service response
  log_file: /var/log/browser-launch/startup.log   # Linux default
  browser_path: /usr/bin/brave-browser             # Linux example
  # browser_path: C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe  # Windows example
```

The `browser_path` setting accepts the path for any supported browser. If omitted, the script auto-detects installed browsers. The legacy `brave_path` key is still supported.

## Usage

```bash
./browser-launch.py              # Run setup wizard or normal operation
./browser-launch.py --run        # Force normal operation (skip wizard)
./browser-launch.py --setup      # Run setup wizard
./browser-launch.py --add-portal # Add new captive portal to config
./browser-launch.py --install    # Install autostart (systemd or Task Scheduler)
./browser-launch.py --uninstall  # Remove autostart
```

On Windows, replace `./browser-launch.py` with `python browser-launch.py`.

## Session Cleanup

On both platforms, rebooting without closing Brave causes it to treat the shutdown as a crash and restore all previous windows. The script handles this automatically before launching:

1. Kills any running Brave processes (`pkill` on Linux, `taskkill` on Windows)
2. Deletes Brave's session files
3. Patches Brave's Preferences to mark the exit as clean

| Platform | Session files location |
|----------|----------------------|
| Linux    | `~/.config/BraveSoftware/Brave-Browser/Default/Sessions/` |
| Windows  | `%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Sessions\` |

This ensures you get a fresh, predictable browser environment on every login with only your configured tabs.

A PID-based lockfile prevents the script from running twice if autostart fires more than once.

## Autostart

### Linux

The recommended approach is a `.desktop` autostart entry at:
```
~/.config/autostart/browser-launch.desktop
```

Alternatively, install a systemd user service via `--install`.

**Managing the systemd service:**
```bash
systemctl --user status browser-launch
systemctl --user disable browser-launch
systemctl --user enable browser-launch
```

### Windows

Install a Task Scheduler task via `--install`. This creates a task that runs at logon with a 20-second delay.

**Managing the task:**
```powershell
schtasks /Query /TN browser-launch
schtasks /Delete /TN browser-launch /F
```

## Adding/Removing Tabs

Edit `~/Documents/Configs/browser-launch.yaml` and add or remove tab entries. Changes take effect on next login or manual run.

### Add a new window
```yaml
windows:
  my_new_window:
    delay: 5
    health_check: true
    tabs:
      - name: "Example Site"
        url: "https://example.com"
```

### Add a tab to an existing window
```yaml
windows:
  Network:
    tabs:
      - name: "New Service"
        url: "http://192.168.1.20:3000"
```

## Health Checks

When enabled for a window, the script checks each URL before opening it. Unreachable services are skipped and logged.

Public HTTPS sites (those starting with `https://www.`, `https://mail.`, or `https://github.`) skip health checks automatically.

This is useful for:
- Local homelab services that may not always be running
- Home automation and monitoring tools
- Development servers

## Logging

| Platform | Default log path |
|----------|-----------------|
| Linux    | `/var/log/browser-launch/startup.log` |
| Linux (fallback) | `~/.local/share/browser-launch/startup.log` |
| Windows  | `%LOCALAPPDATA%\browser-launch\startup.log` |

To create the log directory on Linux:
```bash
sudo mkdir -p /var/log/browser-launch && sudo chown $USER:$USER /var/log/browser-launch
```

On Windows, the log directory is created automatically.

## Captive Portal Setup

The script supports multiple captive portals for different WiFi networks. WiFi detection uses `nmcli` on Linux and `netsh` on Windows.

### Adding Portals

```bash
./browser-launch.py --add-portal
```

### Finding the Button Selector

1. Open the captive portal page in your browser
2. Right-click the "Accept" button → Inspect
3. Look for something like: `<input type="submit" value="Accept">`
4. The selector would be: `input[value="Accept"]`

## Dependencies

The script auto-installs required Python packages:
- `pyyaml` - Configuration file handling
- `requests` - HTTP requests and health checks
- `playwright` - (Optional) Captive portal automation

To install manually:

**Linux:**
```bash
pip3 install --user --break-system-packages pyyaml requests
```

**Windows:**
```powershell
pip install --user pyyaml requests
```

For captive portal support:
```bash
pip install --user playwright
python -m playwright install chromium
```

## Troubleshooting

### Browser doesn't open at login

1. Check the log (see [Logging](#logging) for paths)

2. Try running manually:
   ```bash
   ./browser-launch.py --run
   ```

3. Verify config file exists:
   ```bash
   ls -la ~/Documents/Configs/browser-launch.yaml
   ```
   On Windows: check `%USERPROFILE%\Documents\Configs\browser-launch.yaml`

### Tabs not opening (health check failures)

Check the log to see which services are being skipped.

To temporarily disable health checks for a window:
```yaml
windows:
  Network:
    health_check: false
```

### Config file missing

Run the setup wizard:
```bash
./browser-launch.py --setup
```

### Captive portal not working

1. Verify Playwright is installed:
   ```bash
   python3 -m playwright --version
   ```

2. Check the button selector is correct for your portal page.

3. Increase retry attempts in config:
   ```yaml
   captive_portals:
     - ssid: "My Network"
       max_retries: 5
   ```

## Uninstallation

### Linux

```bash
./browser-launch.py --uninstall
rm ~/Documents/Configs/browser-launch.yaml
rm ~/.config/autostart/browser-launch.desktop
sudo rm /usr/local/bin/browser-launch.py
```

### Windows

```powershell
python browser-launch.py --uninstall
del %USERPROFILE%\Documents\Configs\browser-launch.yaml
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details
