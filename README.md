# Browser Launch

Automate your browser startup on Linux with configurable tabs, health checks, and captive portal handling.

## Features

- 🚀 **Auto-launch at boot** - Opens your browser with organized tabs automatically
- 🏥 **Health checks** - Skip tabs for services that are down
- 📶 **Captive portal support** - Auto-accept WiFi login pages
- 🔧 **Interactive setup** - Easy configuration wizard
- 🌐 **Multi-browser support** - Works with Brave, Firefox, Chrome, Chromium
- 📝 **YAML configuration** - Simple file editing for tab management
- ⚙️ **systemd integration** - Proper service management

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

Your browser will now launch automatically at boot with your configured tabs.

## Configuration

The configuration file is stored at `~/Documents/Coding/Configs/browser-launch.yaml`

### Example Configuration

```yaml
# Captive portal settings (optional)
captive_portals:
  - ssid: "Corporate WiFi"
    url: "https://login.corporate.com/"
    accept_button_selector: 'input[value="Accept"]'
    max_retries: 3
    retry_delay: 2
  
  - ssid: "Starbucks WiFi"
    url: "https://portal.starbucks.com/"
    accept_button_selector: 'button#accept'
    max_retries: 3
    retry_delay: 2

# Browser windows
windows:
  # Development tools
  dev:
    delay: 0
    health_check: true
    tabs:
      - name: "GitHub"
        url: "https://github.com/"
      
      - name: "Local API"
        url: "http://localhost:3000"
      
      - name: "Documentation"
        url: "http://localhost:8080/docs"
  
  # Monitoring
  monitoring:
    delay: 4
    health_check: true
    tabs:
      - name: "Grafana"
        url: "http://192.168.1.10:3000"
      
      - name: "Prometheus"
        url: "http://192.168.1.10:9090"
  
  # General
  general:
    delay: 8
    health_check: false
    tabs:
      - name: "Email"
        url: "https://mail.google.com"
      
      - name: "Calendar"
        url: "https://calendar.google.com"

# General settings
settings:
  wait_before_start: 10          # Wait for desktop environment
  health_check_timeout: 3        # Timeout for service checks
  log_file: "/var/log/browser-launch/startup.log"
  brave_path: "/usr/bin/brave-browser"
```

## Usage

### Run normally
```bash
./browser-launch.py
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

### Force run (skip wizard even if no config)
```bash
./browser-launch.py --run
```

## Managing the Service

### Check service status
```bash
systemctl --user status browser-launch
```

### Disable auto-start
```bash
systemctl --user disable browser-launch
```

### Enable auto-start
```bash
systemctl --user enable browser-launch
```

### View logs
```bash
journalctl --user -u browser-launch
# or
cat ~/.local/share/browser-launch/startup.log
```

## Adding/Removing Tabs

Edit `~/Documents/Coding/Configs/browser-launch.yaml` and add or remove tab entries.

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

### Add a tab to existing window
```yaml
windows:
  dev:
    tabs:
      - name: "New Service"
        url: "http://localhost:5000"
```

Changes take effect on next boot (or next manual run).

## Captive Portal Setup

The script supports **multiple captive portals** for different WiFi networks.

### During Initial Setup

The setup wizard allows you to add one or more captive portals. You can add portals for all the WiFi networks you regularly use (work, coffee shops, home guest network, etc.).

### Adding More Portals Later

When you connect to a new WiFi network with a captive portal:

```bash
./browser-launch.py --add-portal
```

This will:
1. Keep your existing configuration
2. Ask for the new portal details
3. Add it to your config file

### Portal Configuration

For each portal, you need:
- **WiFi network name (SSID)** - Exact name of the network
- **Login page URL** - The captive portal address
- **Accept button selector** - CSS selector for the accept button (default usually works)

The script will automatically accept the terms page before opening your tabs.

### Finding the button selector

1. Open the captive portal page in your browser
2. Right-click the "Accept" button → Inspect
3. Look for the button's HTML, e.g., `<input type="submit" value="Accept">`
4. The selector is `input[value="Accept"]`

## Health Checks

When enabled for a window, the script pings each URL before opening it. If a service is down, that tab is skipped.

This is useful for:
- Local development servers that may not be running
- Home lab services that might be offline
- Network monitoring tools

Public HTTPS sites (like GitHub, Gmail) skip health checks automatically.

## Dependencies

The script auto-installs required Python packages:
- `pyyaml` - Configuration file handling
- `requests` - HTTP requests and health checks
- `playwright` - (Optional) Captive portal automation

## Troubleshooting

### Browser doesn't open at boot

1. Check if service is enabled:
   ```bash
   systemctl --user is-enabled browser-launch
   ```

2. Check service logs:
   ```bash
   journalctl --user -u browser-launch -n 50
   ```

3. Verify config file exists:
   ```bash
   ls -la ~/Documents/Coding/Configs/browser-launch.yaml
   ```

### Config file missing

Run the setup wizard again:
```bash
./browser-launch.py --setup
```

### Tabs not opening

1. Check if health checks are failing:
   ```bash
   cat ~/.local/share/browser-launch/startup.log
   ```

2. Temporarily disable health checks in config:
   ```yaml
   windows:
     my_window:
       health_check: false
   ```

### Captive portal not working

1. Verify Playwright is installed:
   ```bash
   python3 -m playwright --version
   ```

2. Check the button selector is correct
3. Increase retry attempts in config:
   ```yaml
   captive_portal:
     max_retries: 5
   ```

### Permissions error on log file

The script will automatically fallback to `~/.local/share/brave-bootup/startup.log` if it can't write to `/var/log/`.

## Example Use Cases

### Home Lab Dashboard
Open monitoring tools and management interfaces:
- Home Assistant
- Proxmox
- Pi-hole
- pfSense
- Grafana

### Developer Workflow
Launch your development environment:
- Local dev server
- API documentation
- Database admin panel
- GitHub
- Slack

### Media Center
Entertainment tabs:
- YouTube
- Jellyfin/Plex
- Streaming services

### Trading/Finance
Market monitoring:
- Trading platforms
- News sites
- Portfolio trackers
- Market data

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- 🐛 Report bugs: [GitHub Issues](https://github.com/yourusername/browser-launch/issues)
- 💡 Feature requests: [GitHub Discussions](https://github.com/yourusername/browser-launch/discussions)

## Credits

Created by [Your Name]

Inspired by the need to automate repetitive browser setup tasks on Linux systems.
