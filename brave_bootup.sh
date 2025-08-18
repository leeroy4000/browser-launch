#!/usr/bin/env python3
"""
Script: brave_bootup.sh
Purpose: Launches Brave, accepts captive portal login (if on work WiFi), opens multi-tab windows
"""

import os
import time
import subprocess
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ─── Pre-Logging Touchpoint ───────────────────────────────────────────────
try:
    with open("/var/log/brave/startup.log", "a") as log:
        log.write("Script triggered (pre-logging setup)\n")
except Exception:
    pass

# ─── Configuration ────────────────────────────────────────────────────────
LOGFILE = Path("/var/log/brave/startup.log")
BRAVE_PATH = "/usr/bin/brave-browser"
WAIT_BEFORE_START = 10

# ─── Logging Setup ────────────────────────────────────────────────────────
def setup_logging():
    logging.basicConfig(
        filename=LOGFILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

# ─── WiFi SSID Check ──────────────────────────────────────────────────────
def is_work_wifi():
    try:
        ssid_output = subprocess.check_output(
            ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"]
        ).decode()
        for line in ssid_output.splitlines():
            active, ssid = line.split(":")
            if active == "yes" and ssid == "UnityPoint Guest wifi":
                logging.info("✅ Detected UnityPoint Guest WiFi")
                return True
    except Exception as e:
        logging.warning(f"Could not determine SSID: {e}")
    return False

# ─── Captive Portal Flow ──────────────────────────────────────────────────
def launch_and_accept():
    logging.info("Launching UnityPoint login page")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=False,
                executable_path=BRAVE_PATH,
                args=["--start-maximized"]
            )
            page = browser.new_page()
            page.goto("https://guestwifi.unitypoint.org/")
            page.wait_for_selector('input[value="Accept"]', timeout=10000)
            page.click('input[value="Accept"]')
            logging.info("Accepted guest WiFi agreement")
            time.sleep(2)
        except PlaywrightTimeout:
            logging.warning("Accept button not found in time")
        except Exception as e:
            logging.exception(f"Error during captive portal flow: {e}")
        finally:
            browser.close()
            logging.info("Closed initial Brave window")

# ─── Tab Launcher ─────────────────────────────────────────────────────────
def open_tabs(urls, delay=0):
    time.sleep(delay)
    try:
        subprocess.Popen([BRAVE_PATH, "--new-window"] + urls)
        logging.info(f"Launched Brave window with {len(urls)} tab(s): {urls[0]}")
    except Exception as e:
        logging.exception(f"Failed to open tabs: {e}")

# ─── Main Routine ─────────────────────────────────────────────────────────
def main():
    logging.info("brave_bootup started, waiting for environment")
    time.sleep(WAIT_BEFORE_START)

    if is_work_wifi():
        launch_and_accept()
    else:
        logging.info("🛑 Not on UnityPoint Guest WiFi — skipping captive portal flow.")

    open_tabs([
        "https://192.168.1.15:8006/#v1:0:18:4:::::::",      # Proxmox
        "https://192.168.1.24:8006/#v1:0:18:4:::::::",      # Proxmox
        "https://192.168.1.1/",                             # pfSense
        "https://192.168.1.2/admin/",                       # Pi-hole
        "https://192.168.1.13:8043/#dashboard",             # Omada
        "http://192.168.1.26:8123/dashboard-default/0",     # Home Assistant
        "http://192.168.1.14:9000/#!/3/docker/containers"   # Portainer
    ])

    open_tabs(["https://copilot.microsoft.com/"], delay=4)

    open_tabs([
        "https://www.youtube.com/",
        "http://192.168.1.14:8096/web/#/home.html",         # Jellyfin
        "https://www.amazon.com/gp/video/storefront"
    ], delay=8)

    open_tabs([
        "https://mail.proton.me/u/0/inbox",
        "https://wng.org/"
    ], delay=12)

    logging.info("All browser windows launched successfully")

# ─── Entry Point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    setup_logging()

    if "VIRTUAL_ENV" not in os.environ:
        logging.warning("⚠️ Not running inside virtualenv—Playwright may not be available")

    try:
        main()
    except Exception as e:
        logging.exception(f"Unhandled exception occurred: {e}")
