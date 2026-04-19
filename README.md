# Browser Launch

Automate your browser startup on Linux with configurable tabs, health checks, and captive portal handling.

## Features

- 🚀 **Auto-launch at login** - Opens your browser with organized tabs automatically
- 🏥 **Health checks** - Skip tabs for services that are down
- 📶 **Captive portal support** - Auto-accept WiFi login pages
- 🔧 **Interactive setup** - Easy configuration wizard
- 🌐 **Multi-browser support** - Works with Brave, Firefox, Chrome, Chromium
- 📝 **YAML configuration** - Simple file editing for tab management
- ⚙️ **systemd integration** - Optional service management

## Quick Start

### 1. Download the script

```bash
git clone https://github.com/yourusername/browser-launch.git
cd browser-launch
chmod +x browser-launch.py
```

### 2. Run setup wizard

```bash
./browser-launch.py
```

The setup wizard will:
- Detect installed browsers
- Configure captive portal (if needed)
- Set up your tabs and windows
- Install systemd service (optional)

### 3. Done!

Your browser will now launch automatically at login with your configured tabs.

## Configuration

The configuration file is stored at `~/Documents/Configs/browser-launch.yaml`

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
  log_file: /var/log/browser-launch/startup.log
  brave_path: /usr/bin/brave-browser
```

## Usage

### Run normally
```bash
./browser-launch.py
```

### Force run (skip setup wizard)
```bash
./browser-launch.py --run
```

### Run setup wizard again
```bash
./browser-launch.py --setup
```

### Add a new captive portal
```bash
./browser-launch.py --add-portal
```

### Install systemd service
```bash
./browser-launch.py --install
```

### Uninstall systemd service
```bash
./browser-launch.py --uninstall
```

## Autostart

Browser Launch uses a `.desktop` autostart entry by default, which fires at login after the desktop environment is ready. This is the recommended approach for launching a graphical browser.

The autostart file is located at:
```
~/.config/autostart/brave-bootup.desktop
```

Optionally, a systemd user service can be installed instead via `--install`.

## Managing the Service (if installed)

```bash
# Check status
systemctl --user status browser-launch

# Disable auto-start
systemctl --user disable browser-launch

# Enable auto-start
systemctl --user enable browser-launch
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

Logs are written to `/var/log/browser-launch/startup.log` by default.

```bash
cat /var/log/browser-launch/startup.log
```

If `/var/log/browser-launch/` is not writable, the script falls back to:
```
~/.local/share/browser-launch/startup.log
```

To create the log directory with correct permissions:
```bash
sudo mkdir -p /var/log/browser-launch && sudo chown $USER:$USER /var/log/browser-launch
```

## Captive Portal Setup

The script supports multiple captive portals for different WiFi networks.

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
```bash
pip3 install --user --break-system-packages pyyaml requests
```

For captive portal support:
```bash
pip3 install --user --break-system-packages playwright
python3 -m playwright install chromium
```

## Troubleshooting

### Browser doesn't open at login

1. Check the log:
   ```bash
   cat /var/log/browser-launch/startup.log
   ```

2. Try running manually:
   ```bash
   ./browser-launch.py --run
   ```

3. Verify config file exists:
   ```bash
   ls -la ~/Documents/Configs/browser-launch.yaml
   ```

### Tabs not opening (health check failures)

Check the log to see which services are being skipped:
```bash
cat /var/log/browser-launch/startup.log
```

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

```bash
# Remove systemd service (if installed)
./browser-launch.py --uninstall

# Remove config file
rm ~/Documents/Configs/browser-launch.yaml

# Remove autostart entry
rm ~/.config/autostart/brave-bootup.desktop

# Remove script
sudo rm /usr/local/bin/browser-launch.py
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details
