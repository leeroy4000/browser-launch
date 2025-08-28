# 🦁 Brave Bootup Automation Script

This Python script automates the launch of the Brave browser in a multi-tab configuration, with optional captive portal acceptance for UnityPoint Guest WiFi. It’s designed to run at login via autostart and is optimized for home lab and productivity workflows.

## 📌 Purpose

- Detects UnityPoint Guest WiFi and accepts captive portal login
- Launches multiple Brave browser windows with predefined tabs
- Logs activity to `/var/log/brave/startup.log`
- Designed to run inside a Python virtual environment with Playwright

## 🚀 Usage

This script is automatically triggered at login if installed via the companion setup script (`setup_brave_environment.sh`). To run manually:

```bash
~/.brave_env/bin/python /usr/local/bin/brave_bootup.py
```

> ⚠️ Requires Brave browser and Playwright installed in a virtual environment. (See setup_brave_environment.sh repo)


## 📡 Captive Portal Detection

If connected to `UnityPoint Guest wifi`, the script:
- Launches Brave to the login page
- Waits for and clicks the "Accept" button
- Closes the initial window before launching additional windows and tabs

## 🧾 Logging

Logs are written to:

```
/var/log/brave/startup.log
```

Includes:
- WiFi detection status
- Captive portal interaction
- Tab launch confirmations
- Exception traces (if any)

## 🛠 Requirements

- Brave browser installed at `/usr/bin/brave-browser`
- Python 3 with Playwright installed
- NetworkManager (`nmcli`) for SSID detection
- Autostart configured via `.desktop` file (optional)

## ⚙️ Notes

- Script assumes it's running inside a virtual environment (`~/.brave_env`)
- Shebang is auto-updated by the setup script
- Adjust tab URLs in the `main()` function to suit your environment
