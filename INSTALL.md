# Installation Guide

## Prerequisites

- **Linux**: A graphical desktop environment, Python 3.6+
- **Windows**: Python 3.6+ ([python.org](https://www.python.org/downloads/) — check "Add to PATH" during install)
- One of: Brave, Firefox, Chrome, Chromium, or Edge

## Linux Installation

### 1. Download the Script

**Option A: Using git**
```bash
git clone https://github.com/leeroy4000/browser-launch.git
cd browser-launch
```

**Option B: Manual download**
```bash
wget https://raw.githubusercontent.com/leeroy4000/browser-launch/main/browser-launch.py
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

### Optional: systemd Service

If you prefer systemd over the `.desktop` autostart method:

```bash
python3 /usr/local/bin/browser-launch.py --install
```

This installs a systemd user service and removes the `.desktop` autostart file to prevent double-launching.

To verify:
```bash
systemctl --user status browser-launch
```

## Windows Installation

### 1. Download the Script

```powershell
git clone https://github.com/leeroy4000/browser-launch.git
cd browser-launch
```

Or download `browser-launch.py` manually from the repository.

### 2. Run the Setup Wizard

```powershell
python browser-launch.py --setup
```

The wizard will guide you through browser selection, captive portal setup, and tab configuration.

### 3. Set up autostart

Install a Task Scheduler task that runs at logon:

```powershell
python browser-launch.py --install
```

This creates a scheduled task with a 20-second delay after logon.

To verify:
```powershell
schtasks /Query /TN browser-launch
```

That's it — your browser will launch automatically at your next login.

## Configuration File Location

After setup, your configuration is stored at:

| Platform | Path |
|----------|------|
| Linux    | `~/Documents/Configs/browser-launch.yaml` |
| Windows  | `%USERPROFILE%\Documents\Configs\browser-launch.yaml` |

You can edit this file anytime to add, remove, or reorganize tabs and windows. The same config format works on both platforms — only the `browser_path` and `log_file` settings differ.

## Adding More Tabs Later

1. Open the config file in any text editor

2. Add tabs to an existing window:
   ```yaml
   windows:
     Network:
       tabs:
         - name: "New Service"
           url: "http://192.168.1.50:3000"
   ```

3. Save and close — changes take effect on next login (or next manual run)

## Verify Logging

After your first login following installation, check the log to confirm everything ran correctly:

**Linux:**
```bash
cat /var/log/browser-launch/startup.log
```

**Windows:**
```powershell
type %LOCALAPPDATA%\browser-launch\startup.log
```

## Uninstallation

### Linux

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

### Windows

```powershell
# Remove Task Scheduler task
python browser-launch.py --uninstall

# Remove config file
del %USERPROFILE%\Documents\Configs\browser-launch.yaml
```

## Troubleshooting

### "No supported browsers found"

**Linux:**
```bash
# Brave
sudo apt install brave-browser

# Firefox
sudo apt install firefox

# Chromium
sudo apt install chromium-browser
```

**Windows:** Install a browser from its official website. The script checks standard install paths under `Program Files` and `LOCALAPPDATA`.

### "Permission denied" on script (Linux)

```bash
sudo chmod +x /usr/local/bin/browser-launch.py
```

### Dependencies won't install

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

### Browser doesn't open at login

1. Check the log (see [Verify Logging](#verify-logging) for paths)

2. Try running manually:
   ```bash
   python browser-launch.py --run
   ```

3. **Linux:** Verify the autostart file exists:
   ```bash
   cat ~/.config/autostart/browser-launch.desktop
   ```

4. **Windows:** Verify the scheduled task exists:
   ```powershell
   schtasks /Query /TN browser-launch
   ```

### Need help?

- Check the [README](README.md) for full documentation
- Report issues on [GitHub Issues](https://github.com/leeroy4000/browser-launch/issues)
