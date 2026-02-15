# Installation Guide

## Prerequisites

- Linux system with systemd (most modern distributions)
- Python 3.6 or higher
- One of: Brave, Firefox, Chrome, or Chromium browser
- Internet connection

## Step-by-Step Installation

### 1. Download the Script

**Option A: Using git**
```bash
git clone https://github.com/yourusername/browser-launch.git
cd browser-launch
```

**Option B: Manual download**
```bash
# Download the script
wget https://raw.githubusercontent.com/yourusername/browser-launch/main/browser-launch.py

# Make it executable
chmod +x browser-launch.py
```

### 2. Run the Setup Wizard

```bash
./browser-launch.py
```

The wizard will guide you through:
1. Browser selection (auto-detected)
2. Captive portal configuration (optional)
3. Adding tabs and windows
4. systemd service installation (optional)

### 3. That's It!

Your browser will now launch automatically at boot with your configured tabs.

## Post-Installation

### Verify Installation

Check that the systemd service is installed and enabled:
```bash
systemctl --user status browser-launch
```

You should see:
```
● browser-launch.service - Browser Auto-Launch
     Loaded: loaded (/home/user/.config/systemd/user/browser-launch.service; enabled)
     Active: inactive (dead)
```

### Test It

Reboot your system or manually start the service:
```bash
systemctl --user start browser-launch
```

Your browser should open with your configured tabs.

## Configuration File Location

After setup, your configuration is stored at:
```
~/Documents/Coding/Configs/browser-launch.yaml
```

You can edit this file anytime to add/remove tabs.

## Adding More Tabs Later

1. Open the config file:
   ```bash
   nano ~/Documents/Coding/Configs/browser-launch.yaml
   ```

2. Add tabs to an existing window:
   ```yaml
   windows:
     my_window:
       tabs:
         - name: "New Site"
           url: "https://example.com"
   ```

3. Save and close (Ctrl+X, Y, Enter)

4. Changes take effect on next boot (or next manual run)

## Uninstallation

### Remove systemd service only
```bash
./browser-launch.py --uninstall
```

### Complete removal
```bash
# Uninstall service
./browser-launch.py --uninstall

# Remove config file
rm ~/Documents/Coding/Configs/browser-launch.yaml

# Remove script
rm browser-launch.py
```

## Troubleshooting

### "No supported browsers found"

Install a supported browser:
```bash
# Brave
sudo apt install brave-browser

# Firefox
sudo apt install firefox

# Chromium
sudo apt install chromium-browser
```

### "Permission denied"

Make the script executable:
```bash
chmod +x browser-launch.py
```

### Dependencies won't install

The script tries to auto-install dependencies. If that fails:
```bash
pip3 install --user --break-system-packages pyyaml requests
```

For captive portal support:
```bash
pip3 install --user --break-system-packages playwright
python3 -m playwright install chromium
```

### Browser doesn't open at boot

1. Check service status:
   ```bash
   systemctl --user status browser-launch
   ```

2. Check logs:
   ```bash
   journalctl --user -u browser-launch -n 50
   ```

3. Try running manually:
   ```bash
   ./browser-launch.py --run
   ```

### Need help?

- Check the [README](README.md) for detailed documentation
- Report issues on [GitHub Issues](https://github.com/yourusername/browser-launch/issues)

## Next Steps

- Review the [example configuration](config.example.yaml) for ideas
- Read the full [README](README.md) for advanced features
- Customize your tab groups in the config file
