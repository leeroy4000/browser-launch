#!/usr/bin/env python3
"""
Browser Launch - Automated Browser Startup
===========================================
Automates browser launch at system boot with configurable tabs and windows.

Features:
- Interactive setup wizard on first run
- Config file management (YAML)
- Health checks for services
- Captive portal handling
- systemd service installation
- Cross-browser support (Brave, Firefox, Chrome, Chromium)

Repository: https://github.com/yourusername/browser-launch
License: MIT
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
import argparse

# ==============================================================================
# CONSTANTS
# ==============================================================================

VERSION = "2.0.0"
CONFIG_DIR = Path.home() / "Documents" / "Coding" / "Configs"
CONFIG_FILE = CONFIG_DIR / "browser-launch.yaml"
SERVICE_NAME = "browser-launch"

# ==============================================================================
# DEPENDENCY MANAGEMENT
# ==============================================================================

def check_and_install_dependencies():
    """
    Verify required Python packages are installed.
    Attempts to install missing packages automatically.
    """
    required_packages = {
        'yaml': 'pyyaml',
        'requests': 'requests'
    }
    
    # Playwright is optional - only needed for captive portal
    optional_packages = {
        'playwright': 'playwright'
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"📦 Installing missing dependencies: {', '.join(missing)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--user', '--break-system-packages'
            ] + missing, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("Please install manually with:")
            print(f"  pip install --user --break-system-packages {' '.join(missing)}")
            sys.exit(1)

# Check dependencies before importing
check_and_install_dependencies()

# Now import the packages
import yaml
import requests
import urllib3

# Suppress SSL warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try to import playwright (optional)
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# ==============================================================================
# BROWSER DETECTION
# ==============================================================================

def detect_browsers():
    """
    Detect which browsers are installed on the system.
    
    Returns:
        dict: Dictionary of browser names to executable paths
    """
    browsers = {}
    
    browser_paths = {
        'Brave': ['/usr/bin/brave-browser', '/usr/bin/brave', '/snap/bin/brave'],
        'Firefox': ['/usr/bin/firefox', '/snap/bin/firefox'],
        'Chrome': ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable'],
        'Chromium': ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/snap/bin/chromium']
    }
    
    for browser_name, paths in browser_paths.items():
        for path in paths:
            if Path(path).exists():
                browsers[browser_name] = path
                break
    
    return browsers

# ==============================================================================
# CAPTIVE PORTAL MANAGEMENT
# ==============================================================================

def add_captive_portal():
    """
    Add a new captive portal to existing configuration.
    Prompts for portal details and appends to config file.
    """
    # Load existing config
    config = load_config()
    if not config:
        print("❌ No configuration found. Run setup first: ./browser-launch.py --setup")
        sys.exit(1)
    
    print("=" * 70)
    print("  Add New Captive Portal")
    print("=" * 70)
    print()
    print("Configure a new WiFi captive portal.")
    print()
    
    # Check if Playwright is available
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️  Playwright is required for captive portal support.")
        install = input("Install Playwright now? (y/n): ").strip().lower() == 'y'
        if install:
            print("📦 Installing Playwright...")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '--user', 
                    '--break-system-packages', 'playwright'
                ], stdout=subprocess.DEVNULL)
                subprocess.check_call([
                    sys.executable, '-m', 'playwright', 'install', 'chromium'
                ], stdout=subprocess.DEVNULL)
                print("✅ Playwright installed")
            except:
                print("❌ Failed to install Playwright. Cannot add captive portal.")
                sys.exit(1)
        else:
            print("Cannot add captive portal without Playwright.")
            sys.exit(1)
    
    # Get portal details
    print()
    ssid = input("WiFi network name (SSID): ").strip()
    if not ssid:
        print("❌ SSID is required")
        sys.exit(1)
    
    url = input("Captive portal URL: ").strip()
    if not url:
        print("❌ URL is required")
        sys.exit(1)
    
    selector = input("Accept button selector [input[value=\"Accept\"]]: ").strip()
    selector = selector or 'input[value="Accept"]'
    
    # Create new portal config
    new_portal = {
        'ssid': ssid,
        'url': url,
        'accept_button_selector': selector,
        'max_retries': 3,
        'retry_delay': 2
    }
    
    # Update config structure to support multiple portals
    if 'captive_portal' in config and config['captive_portal'].get('enabled'):
        # Old single-portal format - convert to list
        old_portal = config['captive_portal']
        config['captive_portals'] = [
            {
                'ssid': old_portal.get('ssid', ''),
                'url': old_portal.get('url', ''),
                'accept_button_selector': old_portal.get('accept_button_selector', 'input[value="Accept"]'),
                'max_retries': old_portal.get('max_retries', 3),
                'retry_delay': old_portal.get('retry_delay', 2)
            }
        ]
        del config['captive_portal']
    
    # Initialize captive_portals if it doesn't exist
    if 'captive_portals' not in config:
        config['captive_portals'] = []
    
    # Check for duplicate SSID
    for portal in config['captive_portals']:
        if portal['ssid'] == ssid:
            print(f"⚠️  Portal for '{ssid}' already exists. Updating...")
            config['captive_portals'].remove(portal)
            break
    
    # Add new portal
    config['captive_portals'].append(new_portal)
    
    # Save config
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print()
    print(f"✅ Added captive portal for '{ssid}'")
    print(f"   Total portals configured: {len(config['captive_portals'])}")
    print()
    print(f"Config updated: {CONFIG_FILE}")
    print()

# ==============================================================================
# SETUP WIZARD
# ==============================================================================

def run_setup_wizard():
    """
    Interactive setup wizard for first-time configuration.
    Creates config file and optionally installs systemd service.
    """
    print("=" * 70)
    print("  BROWSER LAUNCH - Setup Wizard")
    print("=" * 70)
    print()
    print("Welcome! This wizard will help you configure browser auto-launch.")
    print()
    
    # Detect browsers
    browsers = detect_browsers()
    
    if not browsers:
        print("❌ No supported browsers found!")
        print("Please install one of: Brave, Firefox, Chrome, or Chromium")
        sys.exit(1)
    
    # Browser selection
    print("Detected browsers:")
    browser_list = list(browsers.keys())
    for i, browser in enumerate(browser_list, 1):
        print(f"  {i}. {browser} ({browsers[browser]})")
    print()
    
    while True:
        choice = input(f"Select browser [1-{len(browser_list)}]: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(browser_list):
                selected_browser = browser_list[idx]
                browser_path = browsers[selected_browser]
                break
        except ValueError:
            pass
        print("Invalid selection. Try again.")
    
    print(f"✅ Selected: {selected_browser}")
    print()
    
    # Captive portal configuration
    print("─" * 70)
    print("Captive Portal Configuration (optional)")
    print("─" * 70)
    print("Some WiFi networks require accepting terms before internet access.")
    print("If you connect to such a network, configure it here.")
    print()
    
    captive_enabled = input("Do you use a captive portal WiFi? (y/n): ").strip().lower() == 'y'
    
    captive_portals = []
    
    if captive_enabled:
        if not PLAYWRIGHT_AVAILABLE:
            print("\n⚠️  Playwright is required for captive portal support.")
            install = input("Install Playwright now? (y/n): ").strip().lower() == 'y'
            if install:
                print("📦 Installing Playwright...")
                try:
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install', '--user', 
                        '--break-system-packages', 'playwright'
                    ], stdout=subprocess.DEVNULL)
                    subprocess.check_call([
                        sys.executable, '-m', 'playwright', 'install', 'chromium'
                    ], stdout=subprocess.DEVNULL)
                    print("✅ Playwright installed")
                except:
                    print("❌ Failed to install Playwright. Captive portal disabled.")
                    captive_enabled = False
            else:
                captive_enabled = False
        
        if captive_enabled:
            print()
            ssid = input("WiFi network name (SSID): ").strip()
            url = input("Captive portal URL: ").strip()
            selector = input("Accept button selector [input[value=\"Accept\"]]: ").strip()
            
            captive_portals.append({
                'ssid': ssid,
                'url': url,
                'accept_button_selector': selector or 'input[value="Accept"]',
                'max_retries': 3,
                'retry_delay': 2
            })
            
            # Offer to add more portals
            print()
            while input("Add another captive portal? (y/n): ").strip().lower() == 'y':
                print()
                ssid = input("WiFi network name (SSID): ").strip()
                url = input("Captive portal URL: ").strip()
                selector = input("Accept button selector [input[value=\"Accept\"]]: ").strip()
                
                captive_portals.append({
                    'ssid': ssid,
                    'url': url,
                    'accept_button_selector': selector or 'input[value="Accept"]',
                    'max_retries': 3,
                    'retry_delay': 2
                })
                print(f"✅ Added portal for '{ssid}'")
    
    print()
    print("─" * 70)
    print("Tab Configuration")
    print("─" * 70)
    print("You can add tabs now or edit the config file later.")
    print()
    
    add_tabs = input("Add tabs now? (y/n): ").strip().lower() == 'y'
    
    windows = {}
    
    if add_tabs:
        print("\nYou can organize tabs into separate windows.")
        print("Each window can have a delay before opening.")
        print()
        
        while True:
            window_name = input("Window name (e.g., 'work', 'media') [enter window name or leave blank for next step]: ").strip()
            if not window_name:
                break
            
            delay = input(f"Delay before opening '{window_name}' window (seconds) [0]: ").strip()
            try:
                delay = int(delay) if delay else 0
            except ValueError:
                delay = 0
            
            health_check = input("Enable health checks for this window? (y/n) [y]: ").strip().lower()
            health_check = health_check != 'n'
            
            tabs = []
            print(f"\nAdding tabs to '{window_name}' window:")
            while True:
                url = input("  URL [enter URL or leave blank for next window]: ").strip()
                if not url:
                    break
                name = input("  Tab name: ").strip() or url
                tabs.append({'name': name, 'url': url})
            
            if tabs:
                windows[window_name] = {
                    'delay': delay,
                    'health_check': health_check,
                    'tabs': tabs
                }
            
            print(f"✅ Added {len(tabs)} tab(s) to '{window_name}' window")
            print()
    
    # Create config
    config = {
        'captive_portals': captive_portals,
        'windows': windows,
        'settings': {
            'wait_before_start': 20,
            'health_check_timeout': 3,
            'log_file': '/var/log/browser-launch/startup.log',
            'brave_path': browser_path
        }
    }
    
    # Save config
    print()
    print("─" * 70)
    print("Saving Configuration")
    print("─" * 70)
    
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Configuration saved to: {CONFIG_FILE}")
    print()
    
    # Offer systemd installation
    print("─" * 70)
    print("systemd Service Installation")
    print("─" * 70)
    print("Install as a systemd service to run automatically at boot?")
    print()
    
    install_service = input("Install systemd service? (y/n): ").strip().lower() == 'y'
    
    if install_service:
        install_systemd_service(browser_path)
    
    print()
    print("=" * 70)
    print("  Setup Complete!")
    print("=" * 70)
    print()
    print(f"Config file: {CONFIG_FILE}")
    print(f"You can edit this file anytime to add/remove tabs.")
    print()
    
    if not install_service:
        print("To run manually: ./brave-bootup.py")
        print("To install service later: ./brave-bootup.py --install")
    
    print()

# ==============================================================================
# SYSTEMD SERVICE MANAGEMENT
# ==============================================================================

def install_systemd_service(browser_path):
    """
    Install systemd user service for auto-launch at boot.
    
    Args:
        browser_path (str): Path to browser executable
    """
    script_path = Path(__file__).resolve()
    service_dir = Path.home() / ".config" / "systemd" / "user"
    service_file = service_dir / f"{SERVICE_NAME}.service"
    
    service_content = f"""[Unit]
Description=Browser Auto-Launch
After=graphical-session.target

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 8
ExecStart={sys.executable} {script_path} --run
Environment="DISPLAY=:0"
Environment="XAUTHORITY=%h/.Xauthority"

[Install]
WantedBy=default.target
"""
    
    try:
        # Create service directory
        service_dir.mkdir(parents=True, exist_ok=True)
        
        # Write service file
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        # Reload systemd and enable service
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
        subprocess.run(['systemctl', '--user', 'enable', f'{SERVICE_NAME}.service'], check=True)
        
        print(f"✅ systemd service installed and enabled")
        print(f"   Service file: {service_file}")
        print()
        print("Service will run automatically at next login.")
        print()
        print("Manage with:")
        print(f"  systemctl --user status {SERVICE_NAME}")
        print(f"  systemctl --user disable {SERVICE_NAME}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install systemd service: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def uninstall_systemd_service():
    """Remove systemd user service."""
    service_file = Path.home() / ".config" / "systemd" / "user" / f"{SERVICE_NAME}.service"
    
    try:
        # Disable and stop service
        subprocess.run(['systemctl', '--user', 'disable', f'{SERVICE_NAME}.service'], 
                      stderr=subprocess.DEVNULL)
        subprocess.run(['systemctl', '--user', 'stop', f'{SERVICE_NAME}.service'], 
                      stderr=subprocess.DEVNULL)
        
        # Remove service file
        if service_file.exists():
            service_file.unlink()
        
        # Reload systemd
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
        
        print(f"✅ systemd service uninstalled")
        
    except Exception as e:
        print(f"❌ Error uninstalling service: {e}")

# ==============================================================================
# LOGGING SETUP
# ==============================================================================

def setup_logging(log_file):
    """
    Configure logging to file with timestamps and log levels.
    
    Args:
        log_file (str): Path to log file
    """
    log_path = Path(log_file)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Fallback to home directory if /var/log isn't writable
        log_path = Path.home() / ".local" / "share" / "browser-launch" / "startup.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.info("=" * 60)
    logging.info(f"Browser launch script v{VERSION} started")
    logging.info("=" * 60)

# ==============================================================================
# CONFIGURATION MANAGEMENT
# ==============================================================================

def load_config():
    """
    Load configuration from YAML file.
    
    Returns:
        dict: Configuration dictionary or None if not found
    """
    if not CONFIG_FILE.exists():
        return None
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
        logging.info(f"✅ Loaded configuration from {CONFIG_FILE}")
        return config
    except Exception as e:
        logging.error(f"Failed to load config file: {e}")
        print(f"❌ Error loading config file: {e}")
        return None

# ==============================================================================
# NETWORK DETECTION
# ==============================================================================

def has_internet_connection(timeout=5):
    """
    Check if system has internet connectivity.
    
    Args:
        timeout (int): Connection timeout in seconds
    
    Returns:
        bool: True if connected to internet
    """
    test_urls = [
        'https://www.google.com',
        'https://www.cloudflare.com',
        'https://1.1.1.1'
    ]
    
    for url in test_urls:
        try:
            requests.get(url, timeout=timeout)
            return True
        except:
            continue
    
    return False

def wait_for_internet(max_wait=30, check_interval=5):
    """
    Wait for internet connection with timeout.
    
    Args:
        max_wait (int): Maximum time to wait in seconds
        check_interval (int): Seconds between checks
    
    Returns:
        bool: True if internet available, False if timeout
    """
    elapsed = 0
    while elapsed < max_wait:
        if has_internet_connection():
            logging.info("✅ Internet connection established")
            return True
        
        logging.info(f"Waiting for internet connection... ({elapsed}/{max_wait}s)")
        time.sleep(check_interval)
        elapsed += check_interval
    
    logging.warning(f"⚠️ No internet connection after {max_wait}s")
    return False

def is_target_wifi(ssid):
    """
    Check if connected to specified WiFi network.
    
    Args:
        ssid (str): SSID to check for
    
    Returns:
        bool: True if connected to target SSID
    """
    try:
        ssid_output = subprocess.check_output(
            ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
            stderr=subprocess.DEVNULL
        ).decode()
        
        for line in ssid_output.splitlines():
            if not line:
                continue
            active, current_ssid = line.split(":", 1)
            if active == "yes" and current_ssid == ssid:
                logging.info(f"✅ Connected to target WiFi: {ssid}")
                return True
        
        return False
        
    except:
        return False

# ==============================================================================
# HEALTH CHECK
# ==============================================================================

def is_service_reachable(url, timeout=3):
    """
    Check if a service is reachable via HTTP/HTTPS.
    
    Args:
        url (str): URL to check
        timeout (int): Request timeout in seconds
    
    Returns:
        bool: True if service responds
    """
    try:
        response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return response.status_code < 500
    except:
        return False

# ==============================================================================
# CAPTIVE PORTAL HANDLER
# ==============================================================================

def launch_and_accept(portal_config, browser_path):
    """
    Launch browser and automatically accept captive portal agreement.
    
    Args:
        portal_config (dict): Captive portal configuration
        browser_path (str): Path to browser executable
    
    Returns:
        bool: True if successful
    """
    if not PLAYWRIGHT_AVAILABLE:
        logging.warning("Playwright not available - skipping captive portal")
        return False
    
    url = portal_config['url']
    selector = portal_config['accept_button_selector']
    max_retries = portal_config.get('max_retries', 3)
    retry_delay = portal_config.get('retry_delay', 2)
    
    for attempt in range(1, max_retries + 1):
        logging.info(f"Captive portal attempt {attempt}/{max_retries}")
        
        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(
                    headless=False,
                    executable_path=browser_path,
                    args=["--start-maximized"]
                )
                
                page = browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=15000)
                page.wait_for_selector(selector, timeout=10000)
                page.click(selector)
                logging.info("✅ Accepted captive portal agreement")
                time.sleep(2)
                return True
                
            except:
                logging.warning(f"⚠️ Attempt {attempt} failed")
            finally:
                if browser:
                    browser.close()
        
        if attempt < max_retries:
            time.sleep(retry_delay)
    
    logging.error(f"❌ Failed to accept captive portal after {max_retries} attempts")
    return False

# ==============================================================================
# TAB LAUNCHER
# ==============================================================================

def open_tabs(window_name, tabs, delay=0, health_check=False, timeout=3, browser_path='/usr/bin/brave-browser'):
    """
    Open a new browser window with multiple tabs.
    
    Args:
        window_name (str): Name of window (for logging)
        tabs (list): List of tab dictionaries
        delay (int): Seconds to wait before launching
        health_check (bool): Whether to check service availability
        timeout (int): Health check timeout
        browser_path (str): Path to browser executable
    """
    if delay > 0:
        logging.info(f"Waiting {delay}s before opening {window_name} window")
        time.sleep(delay)
    
    urls_to_open = []
    for tab in tabs:
        name = tab.get('name', 'Unknown')
        url = tab['url']
        
        # Skip health check for public HTTPS sites
        skip_check = (not health_check or 
                     url.startswith('https://www.') or 
                     url.startswith('https://mail.') or 
                     url.startswith('https://github.'))
        
        if skip_check:
            urls_to_open.append(url)
            logging.info(f"  ✓ Queued: {name}")
        else:
            if is_service_reachable(url, timeout):
                urls_to_open.append(url)
                logging.info(f"  ✅ Reachable: {name}")
            else:
                logging.warning(f"  ⏭️  Skipped (unreachable): {name} - {url}")
    
    if urls_to_open:
        try:
            subprocess.Popen([browser_path, "--new-window"] + urls_to_open)
            logging.info(f"✅ Opened {window_name} window with {len(urls_to_open)}/{len(tabs)} tab(s)")
            # Give browser time to process this window before launching the next one
            time.sleep(3)
        except Exception as e:
            logging.exception(f"❌ Failed to open {window_name} window: {e}")
    else:
        logging.warning(f"⚠️ No reachable tabs for {window_name} window")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main script execution."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Browser auto-launch with configurable tabs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./browser-launch.py              Run setup wizard or normal operation
  ./browser-launch.py --run        Force normal operation (skip wizard)
  ./browser-launch.py --install    Install systemd service
  ./browser-launch.py --uninstall  Remove systemd service
  ./browser-launch.py --setup      Run setup wizard
  ./browser-launch.py --add-portal Add new captive portal to config
        """
    )
    parser.add_argument('--run', action='store_true', help='Run browser launch')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--install', action='store_true', help='Install systemd service')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall systemd service')
    parser.add_argument('--add-portal', action='store_true', help='Add a new captive portal to existing config')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    
    args = parser.parse_args()
    
    # Handle explicit commands
    if args.uninstall:
        uninstall_systemd_service()
        return
    
    if args.setup:
        run_setup_wizard()
        return
    
    if args.add_portal:
        add_captive_portal()
        return
    
    if args.install:
        config = load_config()
        if not config:
            print("❌ No configuration found. Run setup first: ./browser-launch.py --setup")
            sys.exit(1)
        browser_path = config.get('settings', {}).get('brave_path', '/usr/bin/brave-browser')
        install_systemd_service(browser_path)
        return
    
    # Load configuration
    config = load_config()
    
    # If no config exists and we're interactive, run setup
    if not config:
        if sys.stdin.isatty():
            print("No configuration found. Running setup wizard...")
            print()
            run_setup_wizard()
            return
        else:
            # Running non-interactively (e.g., from systemd) without config
            logging.error("No configuration file found. Run setup wizard first.")
            sys.exit(1)
    
    # Setup logging
    settings = config.get('settings', {})
    setup_logging(settings.get('log_file', '/var/log/browser-launch/startup.log'))
    
    # Wait for desktop environment
    wait_time = settings.get('wait_before_start', 20)
    logging.info(f"Waiting {wait_time}s for desktop environment")
    time.sleep(wait_time)
    
    # Check for internet if captive portal enabled
    portals = config.get('captive_portals', [])
    
    # Support legacy single portal format
    if not portals and 'captive_portal' in config:
        legacy_portal = config['captive_portal']
        if legacy_portal.get('enabled'):
            portals = [legacy_portal]
    
    if portals:
        if not wait_for_internet(max_wait=30):
            logging.warning("Proceeding without internet connection")
        
        # Find matching portal for current WiFi
        current_ssid = None
        try:
            ssid_output = subprocess.check_output(
                ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
                stderr=subprocess.DEVNULL
            ).decode()
            for line in ssid_output.splitlines():
                if line:
                    active, ssid = line.split(":", 1)
                    if active == "yes":
                        current_ssid = ssid
                        break
        except:
            pass
        
        # Try to handle portal for current network
        if current_ssid:
            portal_found = False
            for portal in portals:
                if portal.get('ssid') == current_ssid:
                    logging.info(f"Found portal config for '{current_ssid}'")
                    browser_path = settings.get('brave_path', '/usr/bin/brave-browser')
                    launch_and_accept(portal, browser_path)
                    portal_found = True
                    break
            
            if not portal_found:
                logging.info(f"No portal config found for '{current_ssid}'")
        else:
            logging.info("Could not determine current WiFi network")
    
    # Launch browser windows
    windows = config.get('windows', {})
    browser_path = settings.get('brave_path', '/usr/bin/brave-browser')
    health_check_timeout = settings.get('health_check_timeout', 3)
    
    for window_name, window_config in windows.items():
        tabs = window_config.get('tabs', [])
        if not tabs:
            continue
        
        open_tabs(
            window_name=window_name,
            tabs=tabs,
            delay=window_config.get('delay', 0),
            health_check=window_config.get('health_check', False),
            timeout=health_check_timeout,
            browser_path=browser_path
        )
    
    logging.info("=" * 60)
    logging.info("Browser startup sequence completed")
    logging.info("=" * 60)

# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # Security check
    if os.geteuid() == 0:
        print("❌ Do not run this script as root.")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.exception(f"Unhandled exception: {e}")
        sys.exit(1)
