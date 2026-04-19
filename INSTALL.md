# Installation Guide

## Prerequisites

- Linux system with a graphical desktop environment
- Python 3.6 or higher
- One of: Brave, Firefox, Chrome, or Chromium browser

## Step-by-Step Installation

### 1. Download the Script

**Option A: Using git**
```bash
git clone https://github.com/yourusername/browser-launch.git
cd browser-launch
```

**Option B: Manual download**
```bash
wget https://raw.githubusercontent.com/yourusername/browser-launch/main/browser-launch.py
chmod +x browser-launch.py
```

### 2. Install to system path (recommended)

```bash
sudo cp browser-launch.py /usr/local/bin/browser-launch.py
sudo chmod +x /usr/local/bin/browser-launch.py
```

### 3. Create the log directory

```bash
sudo mkdir -p /var/log/browser-launch && sudo chown $USER:$USER /var/log/browser-launch
```

### 4. Run the Setup Wizard

```bash
python3 /usr/local/bin/browser-launch.py --setup
```

The wizard will guide you through:
1. Browser selection (auto-detected)
2. Captive portal configuration (optional)
3. Adding tabs and windows

### 5. Set up autostart

Browser Launch uses a `.desktop` autostart entry to launch at login. Create it with:

```bash
cat > ~/.config/autostart/browser-launch.desktop << EOF
[Desktop Entry]
Type=Application
Exec=/usr/local/bin/browser-launch.py --run
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Browser Launch
Comment=Launches browser with configurable tabs and health checks
EOF
```

That's it — your browser will now launch automatically at your next login.

## Configuration File Location

After setup, your configuration is stored at:
```
~/Documents/Configs/browser-launch.yaml
```

You can edit this file anytime to add, remove, or reorganize tabs and windows.

## Adding More Tabs Later

1. Open the config file:
   ```bash
   nano ~/Documents/Configs/browser-launch.yaml
   ```

2. Add tabs to an existing window:
   ```yaml
   windows:
     Network:
       tabs:
         - name: "New Service"
           url: "http://192.168.1.50:3000"
   ```

3. Save and close (Ctrl+X, Y, Enter)

4. Changes take effect on next login (or next manual run)

## Optional: systemd Service

If you prefer systemd over the `.desktop` autostart method:

```bash
python3 /usr/local/bin/browser-launch.py --install
```

This installs a systemd user service and removes the `.desktop` autostart file to prevent double-launching.

To verify:
```bash
systemctl --user status browser-launch
```

## Verify Logging

After your first login following installation, check the log to confirm everything ran correctly:

```bash
cat /var/log/browser-launch/startup.log
```

## Uninstallation

```bash
# Remove autostart entry
rm ~/.config/autostart/browser-launch.desktop

# Remove systemd service (if installed)
python3 /usr/local/bin/browser-launch.py --uninstall

# Remove config file
rm ~/Documents/Configs/browser-launch.yaml

# Remove script
sudo rm /usr/local/bin/browser-launch.py

# Remove log directory (optional)
sudo rm -rf /var/log/browser-launch
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

### "Permission denied" on script

```bash
sudo chmod +x /usr/local/bin/browser-launch.py
```

### Dependencies won't install

```bash
pip3 install --user --break-system-packages pyyaml requests
```

For captive portal support:
```bash
pip3 install --user --break-system-packages playwright
python3 -m playwright install chromium
```

### Browser doesn't open at login

1. Check the log:
   ```bash
   cat /var/log/browser-launch/startup.log
   ```

2. Try running manually:
   ```bash
   python3 /usr/local/bin/browser-launch.py --run
   ```

3. Verify the autostart file exists:
   ```bash
   cat ~/.config/autostart/browser-launch.desktop
   ```

### Need help?

- Check the [README](README.md) for full documentation
- Report issues on [GitHub Issues](https://github.com/yourusername/browser-launch/issues)
