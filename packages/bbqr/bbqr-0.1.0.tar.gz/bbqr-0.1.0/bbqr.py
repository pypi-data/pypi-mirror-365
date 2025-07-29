#!/usr/bin/env python3
"""
🔥 BBQR (Barbequer) - A BBQ-themed Terminal QR Code Generator 🔥
Grill your data into QR codes with smoky perfection!
"""

import os
import sys
import subprocess
import argparse
import platform
import qrcode
import pyperclip
import base64
import time
import webbrowser
import requests
import json
import math
import hashlib
import threading
import tempfile
import datetime
import glob
from PIL import Image
from colorama import Fore, Style, init
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor, as_completed

# Handle pyzbar import with automatic dependency installation
pyzbar = None
try:
    from pyzbar import pyzbar
except ImportError as initial_error:
    # First check if colorama is available for colored output
    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
    except ImportError:
        # Fallback to no colors if colorama isn't available yet
        class FakeColors:
            YELLOW = RED = GREEN = CYAN = ""
        Fore = FakeColors()
    
    print(f"{Fore.YELLOW}📦 zbar library not found. Installing system dependencies...")
    
    # Try to install zbar system dependency
    system = platform.system().lower()
    success = False
    
    try:
        if system == "linux":
            # Try different package managers
            try:
                print(f"{Fore.CYAN}Trying apt-get (Ubuntu/Debian)...")
                subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "libzbar0"], check=True, capture_output=True)
                success = True
                print(f"{Fore.GREEN}✅ Installed libzbar0 via apt-get")
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    print(f"{Fore.CYAN}Trying yum (RHEL/CentOS/Fedora)...")
                    subprocess.run(["sudo", "yum", "install", "-y", "zbar"], check=True, capture_output=True)
                    success = True
                    print(f"{Fore.GREEN}✅ Installed zbar via yum")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        print(f"{Fore.CYAN}Trying pacman (Arch Linux)...")
                        subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "zbar"], check=True, capture_output=True)
                        success = True
                        print(f"{Fore.GREEN}✅ Installed zbar via pacman")
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print(f"{Fore.RED}❌ Could not install zbar automatically.")
                        
        elif system == "darwin":  # macOS
            try:
                print(f"{Fore.CYAN}Trying brew (macOS)...")
                subprocess.run(["brew", "install", "zbar"], check=True, capture_output=True)
                success = True
                print(f"{Fore.GREEN}✅ Installed zbar via brew")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"{Fore.RED}❌ Could not install zbar via brew.")
                
        elif system == "windows":
            print(f"{Fore.YELLOW}⚠️ Windows: QR reading requires manual zbar installation")
            print(f"{Fore.CYAN}  Please visit: https://pypi.org/project/pyzbar/ for instructions")
        
        # If system dependency was installed, try importing pyzbar again
        if success:
            try:
                print(f"{Fore.CYAN}Attempting to import pyzbar again...")
                from pyzbar import pyzbar
                print(f"{Fore.GREEN}🎉 Successfully imported pyzbar after installing system dependencies!")
            except ImportError as e:
                print(f"{Fore.RED}❌ Still cannot import pyzbar after installing system deps: {e}")
                print(f"{Fore.YELLOW}⚠️ QR code reading features will be disabled")
        else:
            print(f"{Fore.YELLOW}⚠️ Could not install system dependencies automatically")
            print(f"{Fore.YELLOW}⚠️ QR code reading features will be disabled")
            print(f"{Fore.CYAN}💡 Manual installation instructions:")
            if system == "linux":
                print(f"{Fore.CYAN}   Ubuntu/Debian: sudo apt-get install libzbar0")
                print(f"{Fore.CYAN}   RHEL/CentOS:   sudo yum install zbar")
                print(f"{Fore.CYAN}   Arch Linux:    sudo pacman -S zbar")
            elif system == "darwin":
                print(f"{Fore.CYAN}   macOS:         brew install zbar")
                
    except Exception as e:
        print(f"{Fore.RED}❌ Exception during automatic installation: {e}")
        print(f"{Fore.YELLOW}⚠️ QR code reading features will be disabled")

# Initialize colorama for cross-platform color support
init(autoreset=True)

class BBQTheme:
    """BBQ-themed messages and styling"""
    
    FIRE = "🔥"
    MEAT = "🥩"
    GRILL = "🍖"
    SMOKE = "💨"
    
    @staticmethod
    def welcome():
        os.system('cls' if platform.system().lower() == 'windows' else 'clear')
        print(f"{Fore.RED}{BBQTheme.FIRE} Welcome to BBQR - The Barbequer! {BBQTheme.FIRE}")
        print(f"{Fore.YELLOW}Time to grill your data into delicious QR codes!")
        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

    @staticmethod
    def success(message):
        print(f"{Fore.GREEN}{BBQTheme.MEAT} {message}")
    
    @staticmethod
    def info(message):
        print(f"{Fore.CYAN}{BBQTheme.SMOKE} {message}")
    
    @staticmethod
    def error(message):
        print(f"{Fore.RED}💥 {message}")
    
    @staticmethod
    def cooking():
        print(f"{Fore.YELLOW}{BBQTheme.GRILL} Firing up the grill...")
        print(f"{Fore.YELLOW}{BBQTheme.SMOKE} Smoking your data into a QR code...")

def get_file_path(prompt, allow_empty=False):
    """Get file path with enhanced path support (no tab completion)"""
    try:
        print(f"{Fore.CYAN}📁 Current directory: {os.getcwd()}")
        print(f"{Fore.CYAN}🏠 Use ~ for home directory, relative/absolute paths supported")
        
        user_input = input(prompt).strip()
        
        if not user_input and not allow_empty:
            return None
        
        if not user_input:
            return ""
        
        # Handle quoted paths (remove quotes)
        if user_input.startswith('"') and user_input.endswith('"'):
            user_input = user_input[1:-1]
        elif user_input.startswith("'") and user_input.endswith("'"):
            user_input = user_input[1:-1]
        
        # Expand user directory (~) and environment variables
        expanded_path = os.path.expanduser(os.path.expandvars(user_input))
        
        # Handle Windows-style forward slashes
        if platform.system().lower() == "windows":
            expanded_path = expanded_path.replace('/', os.sep)
        
        # Convert relative paths to absolute paths for consistency
        if not os.path.isabs(expanded_path):
            expanded_path = os.path.abspath(expanded_path)
        
        return expanded_path
        
    except (EOFError, KeyboardInterrupt):
        print()  # New line after Ctrl+C
        return None

class WiFiManager:
    """Cross-platform WiFi profile manager"""
    
    @staticmethod
    def get_current_os():
        """Get current operating system"""
        return platform.system().lower()
    
    @staticmethod
    def get_saved_wifi_profiles():
        """Get list of saved WiFi profiles based on the operating system"""
        os_name = WiFiManager.get_current_os()
        
        if os_name == "windows":
            return WiFiManager._get_windows_profiles()
        elif os_name == "darwin":  # macOS
            return WiFiManager._get_macos_profiles()
        elif os_name == "linux":
            return WiFiManager._get_linux_profiles()
        else:
            BBQTheme.error(f"Unsupported operating system: {os_name}")
            return []
    
    @staticmethod
    def _get_windows_profiles():
        """Get WiFi profiles on Windows using netsh"""
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                  capture_output=True, text=True, check=True)
            profiles = []
            for line in result.stdout.split('\n'):
                if "All User Profile" in line:
                    profile_name = line.split(':')[1].strip()
                    profiles.append(profile_name)
            return profiles
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            BBQTheme.error(f"Failed to get Windows WiFi profiles: {e}")
            return []
    
    @staticmethod
    def _get_macos_profiles():
        """Get WiFi profiles on macOS using security and networksetup"""
        try:
            # Get known WiFi networks from keychain
            result = subprocess.run([
                'security', 'find-generic-password', '-ga', 'AirPort'
            ], capture_output=True, text=True, stderr=subprocess.STDOUT)
            
            profiles = []
            lines = result.stdout.split('\n')
            for line in lines:
                if '"acct"<blob>=' in line:
                    # Extract network name from security output
                    start = line.find('"acct"<blob>=') + len('"acct"<blob>=')
                    end = line.find('<blob>', start)
                    if end > start:
                        network_name = line[start:end].strip('"')
                        if network_name and network_name not in profiles:
                            profiles.append(network_name)
            
            # Alternative: try to get from system preferences
            if not profiles:
                try:
                    result = subprocess.run([
                        'networksetup', '-listpreferredwirelessnetworks', 'en0'
                    ], capture_output=True, text=True, check=True)
                    
                    for line in result.stdout.split('\n')[1:]:  # Skip header
                        network = line.strip()
                        if network and network not in profiles:
                            profiles.append(network)
                except subprocess.CalledProcessError:
                    pass  # Interface might be different (en1, etc.)
            
            return profiles
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            BBQTheme.error(f"Failed to get macOS WiFi profiles: {e}")
            return []
    
    @staticmethod
    def _get_linux_profiles():
        """Get WiFi profiles on Linux using NetworkManager"""
        try:
            # Try NetworkManager first
            result = subprocess.run(['nmcli', '-t', '-f', 'NAME', 'connection', 'show'], 
                                  capture_output=True, text=True, check=True)
            profiles = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    profiles.append(line.strip())
            return profiles
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # Fallback: try to read from wpa_supplicant config (requires root)
                with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'r') as f:
                    content = f.read()
                    profiles = []
                    for line in content.split('\n'):
                        if line.strip().startswith('ssid='):
                            ssid = line.split('=', 1)[1].strip().strip('"')
                            if ssid not in profiles:
                                profiles.append(ssid)
                    return profiles
            except (FileNotFoundError, PermissionError) as e:
                BBQTheme.error(f"Failed to get Linux WiFi profiles: {e}")
                return []
    
    @staticmethod
    def get_wifi_password(profile_name):
        """Get password for a specific WiFi profile based on OS"""
        os_name = WiFiManager.get_current_os()
        
        if os_name == "windows":
            return WiFiManager._get_windows_password(profile_name)
        elif os_name == "darwin":  # macOS
            return WiFiManager._get_macos_password(profile_name)
        elif os_name == "linux":
            return WiFiManager._get_linux_password(profile_name)
        else:
            BBQTheme.error(f"Password retrieval not supported on {os_name}")
            return None
    
    @staticmethod
    def _get_windows_password(profile_name):
        """Get password for WiFi profile on Windows"""
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'profile', 
                                   f'name="{profile_name}"', 'key=clear'], 
                                  capture_output=True, text=True, check=True)
            for line in result.stdout.split('\n'):
                if "Key Content" in line:
                    return line.split(':')[1].strip()
            return None
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            BBQTheme.error(f"Failed to get Windows password for {profile_name}: {e}")
            return None
    
    @staticmethod
    def _get_macos_password(profile_name):
        """Get password for WiFi profile on macOS"""
        try:
            # Use security command to get password from keychain
            result = subprocess.run([
                'security', 'find-generic-password', '-ga', profile_name, '-w'
            ], capture_output=True, text=True, check=True)
            
            password = result.stdout.strip()
            return password if password else None
        except subprocess.CalledProcessError as e:
            BBQTheme.error(f"Failed to get macOS password for {profile_name}: {e}")
            BBQTheme.info("You may need to allow access to keychain or enter password manually")
            return None
    
    @staticmethod
    def _get_linux_password(profile_name):
        """Get password for WiFi profile on Linux"""
        try:
            # Try NetworkManager first
            result = subprocess.run([
                'nmcli', '-s', '-g', '802-11-wireless-security.psk', 
                'connection', 'show', profile_name
            ], capture_output=True, text=True, check=True)
            
            password = result.stdout.strip()
            return password if password else None
        except subprocess.CalledProcessError:
            try:
                # Fallback: try to read from NetworkManager system connections (requires root)
                import glob
                config_files = glob.glob(f'/etc/NetworkManager/system-connections/{profile_name}*')
                if config_files:
                    with open(config_files[0], 'r') as f:
                        for line in f:
                            if line.strip().startswith('psk='):
                                return line.split('=', 1)[1].strip()
                return None
            except (FileNotFoundError, PermissionError) as e:
                BBQTheme.error(f"Failed to get Linux password for {profile_name}: {e}")
                BBQTheme.info("You may need to run with sudo or enter password manually")
                return None
    
    @staticmethod
    def create_wifi_qr_string(ssid, password, security_type="WPA"):
        """Create WiFi QR code string format"""
        return f"WIFI:T:{security_type};S:{ssid};P:{password};;"

class QRReader:
    """QR code reader and content handler"""
    
    @staticmethod
    def get_pictures_directory():
        """Get the default Pictures directory for the current OS"""
        os_name = platform.system().lower()
        
        if os_name == "windows":
            return os.path.join(os.path.expanduser("~"), "Pictures")
        elif os_name == "darwin":  # macOS
            return os.path.join(os.path.expanduser("~"), "Pictures")
        elif os_name == "linux":
            # Try XDG Pictures directory, fallback to ~/Pictures
            pictures_dir = subprocess.run(
                ['xdg-user-dir', 'PICTURES'], 
                capture_output=True, text=True, check=False
            ).stdout.strip()
            if pictures_dir and os.path.exists(pictures_dir):
                return pictures_dir
            return os.path.join(os.path.expanduser("~"), "Pictures")
        else:
            return os.path.join(os.path.expanduser("~"), "Pictures")
    
    @staticmethod
    def decode_qr(image_path):
        """Decode QR code from image file"""
        try:
            # Open and decode the image
            image = Image.open(image_path)
            decoded_objects = pyzbar.decode(image)
            
            if not decoded_objects:
                return None, "No QR code found in image"
            
            if len(decoded_objects) > 1:
                BBQTheme.info(f"Found {len(decoded_objects)} QR codes, processing the first one")
            
            # Get the first QR code data
            qr_data = decoded_objects[0].data.decode('utf-8')
            return qr_data, None
            
        except Exception as e:
            return None, f"Failed to decode QR code: {e}"
    
    @staticmethod
    def handle_wifi_qr(wifi_data):
        """Handle WiFi QR code data"""
        try:
            # Parse WiFi QR format: WIFI:T:WPA;S:NetworkName;P:Password;;
            if not wifi_data.startswith("WIFI:"):
                return False
                
            # Remove WIFI: prefix and trailing ;;
            params_str = wifi_data[5:].rstrip(';')
            
            # Parse parameters
            params = {}
            for part in params_str.split(';'):
                if ':' in part:
                    key, value = part.split(':', 1)
                    params[key] = value
            
            ssid = params.get('S', 'Unknown Network')
            password = params.get('P', '')
            security_type = params.get('T', 'WPA')
            
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}📶 WIFI QR CODE DETECTED 📶")
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.GREEN}{Style.BRIGHT}Network Name: {Fore.YELLOW}{Style.BRIGHT}{ssid}")
            print(f"{Fore.GREEN}{Style.BRIGHT}Security Type: {Fore.YELLOW}{Style.BRIGHT}{security_type}")
            if password:
                print(f"{Fore.GREEN}{Style.BRIGHT}Password: {Fore.YELLOW}{Style.BRIGHT}{password}")
            else:
                print(f"{Fore.GREEN}{Style.BRIGHT}Password: {Fore.YELLOW}{Style.BRIGHT}Open Network (No password)")
            print(f"{Fore.CYAN}{'='*60}")
            
            # Ask if user wants to connect (Windows only for now)
            if platform.system().lower() == "windows" and password:
                connect = input(f"\n{Fore.WHITE}Would you like to connect to this network? (y/N): ").strip().lower()
                if connect in ['y', 'yes']:
                    try:
                        # Create Windows WiFi profile and connect
                        profile_xml = f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>'''
                        
                        # Save profile to temp file
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                            f.write(profile_xml)
                            temp_profile_path = f.name
                        
                        try:
                            # Add the profile
                            subprocess.run([
                                'netsh', 'wlan', 'add', 'profile', f'filename="{temp_profile_path}"'
                            ], check=True, capture_output=True)
                            
                            # Connect to the network
                            subprocess.run([
                                'netsh', 'wlan', 'connect', f'name="{ssid}"'
                            ], check=True, capture_output=True)
                            
                            BBQTheme.success(f"Successfully connected to {ssid}!")
                            
                        except subprocess.CalledProcessError as e:
                            BBQTheme.error(f"Failed to connect to WiFi: {e}")
                        finally:
                            # Clean up temp file
                            try:
                                os.unlink(temp_profile_path)
                            except:
                                pass
                    except Exception as e:
                        BBQTheme.error(f"Failed to process WiFi connection: {e}")
            else:
                BBQTheme.info("WiFi connection is only supported on Windows with password-protected networks")
                
            return True
            
        except Exception as e:
            BBQTheme.error(f"Failed to parse WiFi QR code: {e}")
            return False
    
    @staticmethod
    def handle_image_qr(image_data):
        """Handle image QR code data (base64)"""
        try:
            if not image_data.startswith("data:image"):
                return False
            
            # Extract base64 data
            header, base64_data = image_data.split(',', 1)
            
            # Determine file extension from header
            if 'png' in header:
                ext = '.png'
            elif 'jpeg' in header or 'jpg' in header:
                ext = '.jpg'
            elif 'gif' in header:
                ext = '.gif'
            else:
                ext = '.png'  # Default
            
            # Decode base64 data
            image_bytes = base64.b64decode(base64_data)
            
            # Get Pictures directory
            pictures_dir = QRReader.get_pictures_directory()
            os.makedirs(pictures_dir, exist_ok=True)
            
            # Generate unique filename
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bbqr_decoded_image_{timestamp}{ext}"
            output_path = os.path.join(pictures_dir, filename)
            
            # Save image
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}🖼️ IMAGE QR CODE DETECTED 🖼️")
            print(f"{Fore.CYAN}{'='*60}")
            BBQTheme.success(f"Image extracted and saved!")
            BBQTheme.info(f"📁 Location: {output_path}")
            print(f"{Fore.CYAN}{'='*60}")
            
            return True
            
        except Exception as e:
            BBQTheme.error(f"Failed to handle image QR code: {e}")
            return False
    
    @staticmethod
    def handle_text_qr(text_data):
        """Handle text/URL QR code data"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}{Style.BRIGHT}📝 QR CODE CONTENT:")
        print(f"{Fore.YELLOW}{Style.BRIGHT}{text_data}")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Check if it's a URL
        if text_data.startswith(('http://', 'https://', 'ftp://')):
            print(f"\n{Fore.MAGENTA}🌐 This is a URL")
            
            # Ask if user wants to open in browser or copy to clipboard
            print(f"\n{Fore.CYAN}What would you like to do?")
            print(f"{Fore.YELLOW}1. Open in browser")
            print(f"{Fore.YELLOW}2. Copy to clipboard")
            print(f"{Fore.YELLOW}3. Both")
            print(f"{Fore.YELLOW}4. Nothing")
            
            choice = input(f"\n{Fore.WHITE}Choose (1-4): ").strip()
            
            if choice in ['1', '3']:
                try:
                    webbrowser.open(text_data)
                    BBQTheme.success("URL opened in default browser! 🌐")
                except Exception as e:
                    BBQTheme.error(f"Failed to open URL in browser: {e}")
            
            if choice in ['2', '3']:
                try:
                    pyperclip.copy(text_data)
                    BBQTheme.success("URL copied to clipboard! 📋")
                except Exception as e:
                    BBQTheme.error(f"Failed to copy to clipboard: {e}")
                    
        else:
            # Ask if user wants to copy to clipboard
            copy_choice = input(f"\n{Fore.WHITE}Copy text to clipboard? (y/N): ").strip().lower()
            if copy_choice in ['y', 'yes']:
                try:
                    pyperclip.copy(text_data)
                    BBQTheme.success("Text copied to clipboard! 📋")
                except Exception as e:
                    BBQTheme.error(f"Failed to copy to clipboard: {e}")
        
        return True
    
    @staticmethod
    def handle_file_upload_qr(upload_data):
        """Handle file upload QR code data"""
        try:
            if not upload_data.startswith("BBQR_FILE:"):
                return False
            
            json_str = upload_data[10:]
            upload_info = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['type', 'filename', 'size', 'hash']
            if not all(field in upload_info for field in required_fields):
                BBQTheme.error("Invalid file upload QR code format")
                return False
            
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}📁 FILE UPLOAD QR CODE 📁")
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.GREEN}{Style.BRIGHT}Filename: {Fore.YELLOW}{Style.BRIGHT}{upload_info['filename']}")
            print(f"{Fore.GREEN}{Style.BRIGHT}Size: {Fore.YELLOW}{Style.BRIGHT}{FileUploader.format_size(upload_info['size'])}")
            print(f"{Fore.GREEN}{Style.BRIGHT}Type: {Fore.YELLOW}{Style.BRIGHT}{upload_info['type']}")
            
            if upload_info['type'] == 'chunked':
                print(f"{Fore.GREEN}{Style.BRIGHT}Chunks: {Fore.YELLOW}{Style.BRIGHT}{upload_info['chunks']}")
            
            print(f"{Fore.GREEN}{Style.BRIGHT}Hash: {Fore.YELLOW}{Style.BRIGHT}{upload_info['hash'][:16]}...")
            print(f"{Fore.CYAN}{'='*60}")
            
            # Ask if user wants to download
            download_choice = input(f"\n{Fore.WHITE}Download this file? (y/N): ").strip().lower()
            if download_choice in ['y', 'yes']:
                output_dir = get_file_path(f"{Fore.YELLOW}Enter download directory (press Enter for current): ", allow_empty=True)
                if not output_dir:
                    output_dir = os.getcwd()
                
                if not os.path.exists(output_dir):
                    try:
                        os.makedirs(output_dir, exist_ok=True)
                        BBQTheme.info(f"📁 Created directory: {output_dir}")
                    except Exception as e:
                        BBQTheme.error(f"Failed to create directory: {e}")
                        return True
                
                # Download and reassemble
                result_path = FileUploader.download_and_reassemble(upload_info, output_dir)
                if result_path:
                    BBQTheme.success(f"🎉 File downloaded successfully!")
                    BBQTheme.info(f"📍 Location: {result_path}")
                else:
                    BBQTheme.error("❌ Download failed!")
            else:
                BBQTheme.info("Download cancelled")
            
            return True
            
        except json.JSONDecodeError as e:
            BBQTheme.error(f"Failed to parse file upload QR code: Invalid JSON - {e}")
            return False
        except Exception as e:
            BBQTheme.error(f"Failed to handle file upload QR code: {e}")
            return False

class ProgressTracker:
    """Thread-safe progress tracker for uploads and downloads"""
    
    def __init__(self, total_chunks, operation="Upload"):
        self.total_chunks = total_chunks
        self.completed_chunks = 0
        self.failed_chunks = 0
        self.operation = operation
        self.lock = threading.Lock()
        self.start_time = time.time()
    
    def update_progress(self, success=True):
        """Update progress and display progress bar"""
        with self.lock:
            if success:
                self.completed_chunks += 1
            else:
                self.failed_chunks += 1
            
            total_processed = self.completed_chunks + self.failed_chunks
            progress_percent = (total_processed / self.total_chunks) * 100
            
            # Create progress bar
            bar_width = 40
            filled = int(bar_width * total_processed / self.total_chunks)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            # Calculate elapsed time and ETA
            elapsed = time.time() - self.start_time
            if total_processed > 0:
                avg_time_per_chunk = elapsed / total_processed
                remaining_chunks = self.total_chunks - total_processed
                eta = avg_time_per_chunk * remaining_chunks
                eta_str = f" | ETA: {eta:.1f}" if eta > 0 else ""
            else:
                eta_str = ""
            
            # Display progress
            status = f"\r🔥 {self.operation} Progress: [{bar}] {progress_percent:.1f}% ({total_processed}/{self.total_chunks}){eta_str}"
            print(status, end='', flush=True)
            
            # Print newline when complete
            if total_processed >= self.total_chunks:
                print()  # New line after completion
    
    def is_complete(self):
        """Check if all chunks are processed"""
        with self.lock:
            return (self.completed_chunks + self.failed_chunks) >= self.total_chunks
    
    def get_stats(self):
        """Get current stats"""
        with self.lock:
            return self.completed_chunks, self.failed_chunks, self.total_chunks

class FileUploader:
    """File uploader for 0x0.st service with chunking support"""
    
    UPLOAD_URL = "https://0x0.st"
    MAX_CHUNK_SIZE = 512 * 1024 * 1024  # 512 MiB
    
    @staticmethod
    def get_file_size(file_path):
        """Get file size in bytes"""
        return os.path.getsize(file_path)
    
    @staticmethod
    def format_size(bytes_size):
        """Format bytes to human readable string"""
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PiB"
    
    @staticmethod
    def calculate_chunks(file_size):
        """Calculate number of chunks needed"""
        return math.ceil(file_size / FileUploader.MAX_CHUNK_SIZE)
    
    @staticmethod
    def split_file(file_path, output_dir=None):
        """Split file into chunks if needed"""
        file_size = FileUploader.get_file_size(file_path)
        
        if file_size <= FileUploader.MAX_CHUNK_SIZE:
            # File is small enough, no splitting needed
            return [file_path]
        
        # Create output directory for chunks
        if not output_dir:
            file_dir = os.path.dirname(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            output_dir = os.path.join(file_dir, f"{file_name}_chunks")
        
        os.makedirs(output_dir, exist_ok=True)
        
        chunk_count = FileUploader.calculate_chunks(file_size)
        chunk_paths = []
        
        BBQTheme.info(f"📦 Splitting file into {chunk_count} chunks...")
        BBQTheme.info(f"📁 Chunks will be saved to: {output_dir}")
        
        with open(file_path, 'rb') as input_file:
            for chunk_num in range(chunk_count):
                chunk_filename = f"chunk_{chunk_num:03d}.part"
                chunk_path = os.path.join(output_dir, chunk_filename)
                
                with open(chunk_path, 'wb') as chunk_file:
                    remaining = min(FileUploader.MAX_CHUNK_SIZE, file_size - chunk_num * FileUploader.MAX_CHUNK_SIZE)
                    while remaining > 0:
                        buffer_size = min(8192, remaining)  # 8KB buffer
                        data = input_file.read(buffer_size)
                        if not data:
                            break
                        chunk_file.write(data)
                        remaining -= len(data)
                
                chunk_paths.append(chunk_path)
                BBQTheme.success(f"✅ Created chunk {chunk_num + 1}/{chunk_count}: {chunk_filename}")
        
        return chunk_paths
    
    @staticmethod
    def upload_file(file_path, use_secret=True, expires_hours=None):
        """Upload a file to 0x0.st"""
        try:
            BBQTheme.info(f"🚀 Uploading: {os.path.basename(file_path)}")
            
            # Prepare the request
            files = {'file': open(file_path, 'rb')}
            data = {}
            headers = {
                'User-Agent': 'BBQR File Upload Tool/1.0 (https://github.com/foglomon/bbqr)'
            }
            
            if use_secret:
                data['secret'] = ''  # Empty secret for hard-to-guess URLs
            
            if expires_hours:
                data['expires'] = str(expires_hours)
            
            # Upload the file
            response = requests.post(FileUploader.UPLOAD_URL, files=files, data=data, headers=headers, timeout=300)
            files['file'].close()
            
            if response.status_code == 200:
                upload_url = response.text.strip()
                BBQTheme.success(f"✅ Upload successful!")
                BBQTheme.info(f"🔗 URL: {upload_url}")
                return upload_url
            else:
                BBQTheme.error(f"Upload failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            BBQTheme.error(f"Network error during upload: {e}")
            return None
        except Exception as e:
            BBQTheme.error(f"Upload failed: {e}")
            return None
    
    @staticmethod
    def upload_chunk_worker(chunk_info, progress_tracker=None):
        """Worker function for parallel chunk uploads"""
        chunk_path, chunk_num, total_chunks, use_secret, expires_hours = chunk_info
        try:
            chunk_filename = os.path.basename(chunk_path)
            
            # Prepare the request
            with open(chunk_path, 'rb') as f:
                files = {'file': f}
                data = {}
                headers = {
                    'User-Agent': 'BBQR File Upload Tool/1.0 (https://github.com/foglomon/bbqr)'
                }
                
                if use_secret:
                    data['secret'] = ''  # Empty secret for hard-to-guess URLs
                
                if expires_hours:
                    data['expires'] = str(expires_hours)
                
                # Upload the chunk
                response = requests.post(FileUploader.UPLOAD_URL, files=files, data=data, headers=headers, timeout=300)
            
            if response.status_code == 200:
                upload_url = response.text.strip()
                if progress_tracker:
                    progress_tracker.update_progress(success=True)
                else:
                    BBQTheme.success(f"✅ Chunk {chunk_num + 1}/{total_chunks} uploaded successfully ({chunk_filename})")
                return chunk_num, upload_url
            else:
                if progress_tracker:
                    progress_tracker.update_progress(success=False)
                else:
                    BBQTheme.error(f"❌ Chunk {chunk_num + 1}/{total_chunks} upload failed with status {response.status_code}: {response.text}")
                return chunk_num, None
                
        except requests.exceptions.RequestException as e:
            if progress_tracker:
                progress_tracker.update_progress(success=False)
            else:
                BBQTheme.error(f"❌ Chunk {chunk_num + 1}/{total_chunks} network error: {e}")
            return chunk_num, None
        except Exception as e:
            if progress_tracker:
                progress_tracker.update_progress(success=False)
            else:
                BBQTheme.error(f"❌ Chunk {chunk_num + 1}/{total_chunks} upload error: {e}")
            return chunk_num, None
    
    @staticmethod
    def upload_file_chunked(file_path, use_secret=True, expires_hours=None):
        """Upload file, splitting into chunks if necessary"""
        try:
            file_size = FileUploader.get_file_size(file_path)
            original_filename = os.path.basename(file_path)
            
            BBQTheme.info(f"🔥 Preparing to upload: {original_filename}")
            BBQTheme.info(f"📏 Total size: {FileUploader.format_size(file_size)}")
            
            # Generate file hash for integrity
            file_hash = FileUploader.calculate_file_hash(file_path)
            BBQTheme.info(f"🔐 File hash (SHA256): {file_hash}")
            
            # Split file if necessary
            chunk_paths = FileUploader.split_file(file_path)
            
            if len(chunk_paths) == 1:
                # Single file upload
                BBQTheme.info("📤 Single file upload (no chunking needed)")
                url = FileUploader.upload_file(file_path, use_secret, expires_hours)
                if url:
                    return {
                        'type': 'single',
                        'filename': original_filename,
                        'size': file_size,
                        'hash': file_hash,
                        'url': url
                    }
                return None
            else:
                # Multi-chunk upload with parallel connections
                BBQTheme.info(f"📤 Multi-chunk upload ({len(chunk_paths)} parts)")
                chunk_info = {
                    'type': 'chunked',
                    'filename': original_filename,
                    'size': file_size,
                    'hash': file_hash,
                    'chunks': len(chunk_paths),
                    'urls': [None] * len(chunk_paths)  # Pre-allocate with None values
                }
                
                # Get chunk directory for cleanup
                chunk_dir = os.path.dirname(chunk_paths[0]) if len(chunk_paths) > 1 else None
                
                try:
                    # Prepare chunk upload tasks
                    upload_tasks = []
                    for i, chunk_path in enumerate(chunk_paths):
                        task_info = (chunk_path, i, len(chunk_paths), use_secret, expires_hours)
                        upload_tasks.append(task_info)
                    
                    # Create progress tracker
                    progress_tracker = ProgressTracker(len(chunk_paths), "Upload")
                    
                    # Upload chunks in parallel using ThreadPoolExecutor
                    max_workers = min(len(chunk_paths), 4)  # Limit to 4 concurrent uploads to be respectful
                    BBQTheme.info(f"🔥 Starting parallel uploads with {max_workers} worker threads...")
                    
                    successful_uploads = 0
                    failed_uploads = []
                    
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # Submit all upload tasks
                        future_to_chunk = {executor.submit(FileUploader.upload_chunk_worker, task, progress_tracker): task for task in upload_tasks}
                        
                        # Process completed uploads
                        for future in as_completed(future_to_chunk):
                            try:
                                chunk_num, chunk_url = future.result()
                                if chunk_url:
                                    chunk_info['urls'][chunk_num] = chunk_url
                                    successful_uploads += 1
                                else:
                                    failed_uploads.append(chunk_num + 1)
                            except Exception as e:
                                task_info = future_to_chunk[future]
                                chunk_num = task_info[1]
                                failed_uploads.append(chunk_num + 1)
                                BBQTheme.error(f"❌ Exception in chunk {chunk_num + 1} upload: {e}")
                    
                    # Get final stats
                    completed, failed, total = progress_tracker.get_stats()
                    
                    # Check if all uploads succeeded
                    if failed_uploads:
                        BBQTheme.error(f"❌ Failed to upload chunks: {', '.join(map(str, failed_uploads))}")
                        BBQTheme.error("Upload aborted due to chunk failures")
                        return None
                    
                    BBQTheme.success(f"🎉 All {len(chunk_paths)} chunks uploaded successfully")
                    BBQTheme.info(f"📊 Upload completed: {completed} successful, {failed} failed")
                    
                    return chunk_info
                    
                finally:
                    # Always clean up local chunk files, even on failure
                    try:
                        if len(chunk_paths) > 1:  # Only clean up if we actually created chunks
                            BBQTheme.info("🧹 Cleaning up temporary chunk files...")
                            for chunk_path in chunk_paths:
                                if os.path.exists(chunk_path):
                                    os.remove(chunk_path)
                            if chunk_dir and os.path.exists(chunk_dir) and not os.listdir(chunk_dir):
                                os.rmdir(chunk_dir)
                                BBQTheme.success("🧹 Temporary chunk directory removed")
                            else:
                                BBQTheme.success("🧹 Temporary chunk files cleaned up")
                    except Exception as e:
                        BBQTheme.error(f"Warning: Failed to clean up chunk files: {e}")
                
        except Exception as e:
            BBQTheme.error(f"Chunked upload failed: {e}")
            return None
    
    @staticmethod
    def calculate_file_hash(file_path):
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    @staticmethod
    def download_file(url, output_path):
        """Download a file from URL"""
        try:
            BBQTheme.info(f"📥 Downloading: {url}")
            headers = {
                'User-Agent': 'BBQR File Download Tool/1.0 (https://github.com/bbqr/bbqr)'
            }
            response = requests.get(url, stream=True, headers=headers, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r📦 Progress: {progress:.1f}% ({FileUploader.format_size(downloaded)}/{FileUploader.format_size(total_size)})", end='', flush=True)
            
            if total_size > 0:
                print()  # New line after progress
            
            BBQTheme.success(f"✅ Downloaded: {os.path.basename(output_path)}")
            return True
            
        except requests.exceptions.RequestException as e:
            BBQTheme.error(f"Download failed: {e}")
            return False
        except Exception as e:
            BBQTheme.error(f"Download error: {e}")
            return False
    
    @staticmethod
    def download_chunk_worker(download_info, progress_tracker=None):
        """Worker function for parallel chunk downloads"""
        url, chunk_path, chunk_num, total_chunks = download_info
        try:
            chunk_filename = os.path.basename(chunk_path)
            
            headers = {
                'User-Agent': 'BBQR File Download Tool/1.0 (https://github.com/bbqr/bbqr)'
            }
            response = requests.get(url, stream=True, headers=headers, timeout=300)
            response.raise_for_status()
            
            with open(chunk_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if progress_tracker:
                progress_tracker.update_progress(success=True)
            else:
                BBQTheme.success(f"✅ Downloaded chunk {chunk_num + 1}/{total_chunks} ({chunk_filename})")
            return chunk_num, chunk_path
            
        except requests.exceptions.RequestException as e:
            if progress_tracker:
                progress_tracker.update_progress(success=False)
            else:
                BBQTheme.error(f"❌ Chunk {chunk_num + 1}/{total_chunks} download failed: {e}")
            return chunk_num, None
        except Exception as e:
            if progress_tracker:
                progress_tracker.update_progress(success=False)
            else:
                BBQTheme.error(f"❌ Chunk {chunk_num + 1}/{total_chunks} download error: {e}")
            return chunk_num, None
    
    @staticmethod
    def download_and_reassemble(upload_info, output_dir=None):
        """Download and reassemble chunked files"""
        try:
            if upload_info['type'] == 'single':
                # Single file download
                if not output_dir:
                    output_dir = os.getcwd()
                
                output_path = os.path.join(output_dir, upload_info['filename'])
                if FileUploader.download_file(upload_info['url'], output_path):
                    # Verify hash
                    downloaded_hash = FileUploader.calculate_file_hash(output_path)
                    if downloaded_hash == upload_info['hash']:
                        BBQTheme.success("✅ File integrity verified!")
                        return output_path
                    else:
                        BBQTheme.error("❌ File integrity check failed!")
                        BBQTheme.error(f"Expected: {upload_info['hash']}")
                        BBQTheme.error(f"Got:      {downloaded_hash}")
                        return None
                return None
            
            elif upload_info['type'] == 'chunked':
                # Multi-chunk download and reassembly
                if not output_dir:
                    output_dir = os.getcwd()
                
                temp_dir = os.path.join(output_dir, f"temp_chunks_{int(time.time())}")
                os.makedirs(temp_dir, exist_ok=True)
                
                BBQTheme.info(f"📦 Downloading {upload_info['chunks']} chunks in parallel...")
                
                # Prepare download tasks
                download_tasks = []
                expected_chunk_paths = []
                for i, url in enumerate(upload_info['urls']):
                    chunk_filename = f"chunk_{i:03d}.part"
                    chunk_path = os.path.join(temp_dir, chunk_filename)
                    expected_chunk_paths.append(chunk_path)
                    task_info = (url, chunk_path, i, len(upload_info['urls']))
                    download_tasks.append(task_info)
                
                try:
                    # Create progress tracker
                    progress_tracker = ProgressTracker(len(upload_info['urls']), "Download")
                    
                    # Download chunks in parallel
                    max_workers = min(len(upload_info['urls']), 4)  # Limit concurrent downloads
                    BBQTheme.info(f"🔥 Starting parallel downloads with {max_workers} worker threads...")
                    
                    downloaded_chunks = [None] * len(upload_info['urls'])
                    successful_downloads = 0
                    failed_downloads = []
                    
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # Submit all download tasks
                        future_to_chunk = {executor.submit(FileUploader.download_chunk_worker, task, progress_tracker): task for task in download_tasks}
                        
                        # Process completed downloads
                        for future in as_completed(future_to_chunk):
                            try:
                                chunk_num, chunk_path = future.result()
                                if chunk_path:
                                    downloaded_chunks[chunk_num] = chunk_path
                                    successful_downloads += 1
                                else:
                                    failed_downloads.append(chunk_num + 1)
                            except Exception as e:
                                task_info = future_to_chunk[future]
                                chunk_num = task_info[2]
                                failed_downloads.append(chunk_num + 1)
                                BBQTheme.error(f"❌ Exception in chunk {chunk_num + 1} download: {e}")
                    
                    # Get final stats
                    completed, failed, total = progress_tracker.get_stats()
                    
                    # Check if all downloads succeeded
                    if failed_downloads:
                        BBQTheme.error(f"❌ Failed to download chunks: {', '.join(map(str, failed_downloads))}")
                        return None
                    
                    BBQTheme.success(f"🎉 All {len(upload_info['urls'])} chunks downloaded successfully in parallel!")
                    BBQTheme.info(f"📊 Download completed: {completed} successful, {failed} failed")
                    chunk_paths = downloaded_chunks
                    
                    # Reassemble chunks
                    output_path = os.path.join(output_dir, upload_info['filename'])
                    BBQTheme.info(f"🔧 Reassembling chunks into: {upload_info['filename']}")
                    
                    with open(output_path, 'wb') as output_file:
                        for i, chunk_path in enumerate(chunk_paths):
                            BBQTheme.info(f"🔗 Merging chunk {i + 1}/{len(chunk_paths)}")
                            with open(chunk_path, 'rb') as chunk_file:
                                while True:
                                    data = chunk_file.read(8192)
                                    if not data:
                                        break
                                    output_file.write(data)
                    
                    # Verify file integrity
                    BBQTheme.info("🔐 Verifying file integrity...")
                    downloaded_hash = FileUploader.calculate_file_hash(output_path)
                    if downloaded_hash == upload_info['hash']:
                        BBQTheme.success("✅ File integrity verified!")
                        BBQTheme.success(f"📁 File reassembled: {output_path}")
                        BBQTheme.info(f"📏 Size: {FileUploader.format_size(upload_info['size'])}")
                        return output_path
                    else:
                        BBQTheme.error("❌ File integrity check failed!")
                        BBQTheme.error(f"Expected: {upload_info['hash']}")
                        BBQTheme.error(f"Got:      {downloaded_hash}")
                        if os.path.exists(output_path):
                            os.remove(output_path)
                        return None
                        
                finally:
                    # Always clean up temporary chunks
                    try:
                        BBQTheme.info("🧹 Cleaning up temporary download files...")
                        for chunk_path in downloaded_chunks:
                            if chunk_path and os.path.exists(chunk_path):
                                os.remove(chunk_path)
                        if os.path.exists(temp_dir):
                            os.rmdir(temp_dir)
                        BBQTheme.success("🧹 Temporary download files cleaned up")
                    except Exception as e:
                        BBQTheme.error(f"Warning: Failed to clean up temporary files: {e}")
                
                # Download chunks in parallel
                max_workers = min(len(upload_info['urls']), 4)  # Limit concurrent downloads
                BBQTheme.info(f"� Starting parallel downloads with {max_workers} worker threads...")
                
                downloaded_chunks = [None] * len(upload_info['urls'])
                successful_downloads = 0
                failed_downloads = []
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all download tasks
                    future_to_chunk = {executor.submit(FileUploader.download_chunk_worker, task): task for task in download_tasks}
                    
                    # Process completed downloads
                    for future in as_completed(future_to_chunk):
                        try:
                            chunk_num, chunk_path = future.result()
                            if chunk_path:
                                downloaded_chunks[chunk_num] = chunk_path
                                successful_downloads += 1
                            else:
                                failed_downloads.append(chunk_num + 1)
                        except Exception as e:
                            task_info = future_to_chunk[future]
                            chunk_num = task_info[2]
                            failed_downloads.append(chunk_num + 1)
                            BBQTheme.error(f"❌ Exception in chunk {chunk_num + 1} download: {e}")
                
                # Check if all downloads succeeded
                if failed_downloads:
                    BBQTheme.error(f"❌ Failed to download chunks: {', '.join(map(str, failed_downloads))}")
                    # Clean up partial downloads
                    for chunk_path in downloaded_chunks:
                        if chunk_path and os.path.exists(chunk_path):
                            os.remove(chunk_path)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                    return None
                
                BBQTheme.success(f"🎉 All {len(upload_info['urls'])} chunks downloaded successfully in parallel!")
                chunk_paths = downloaded_chunks
                
                # Reassemble chunks
                output_path = os.path.join(output_dir, upload_info['filename'])
                BBQTheme.info(f"🔧 Reassembling chunks into: {upload_info['filename']}")
                
                with open(output_path, 'wb') as output_file:
                    for i, chunk_path in enumerate(chunk_paths):
                        BBQTheme.info(f"🔗 Merging chunk {i + 1}/{len(chunk_paths)}")
                        with open(chunk_path, 'rb') as chunk_file:
                            while True:
                                data = chunk_file.read(8192)
                                if not data:
                                    break
                                output_file.write(data)
                
                # Clean up temporary chunks
                for chunk_path in chunk_paths:
                    if os.path.exists(chunk_path):
                        os.remove(chunk_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
                
                # Verify file integrity
                BBQTheme.info("🔐 Verifying file integrity...")
                downloaded_hash = FileUploader.calculate_file_hash(output_path)
                if downloaded_hash == upload_info['hash']:
                    BBQTheme.success("✅ File integrity verified!")
                    BBQTheme.success(f"📁 File reassembled: {output_path}")
                    BBQTheme.info(f"📏 Size: {FileUploader.format_size(upload_info['size'])}")
                    return output_path
                else:
                    BBQTheme.error("❌ File integrity check failed!")
                    BBQTheme.error(f"Expected: {upload_info['hash']}")
                    BBQTheme.error(f"Got:      {downloaded_hash}")
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    return None
            
            else:
                BBQTheme.error(f"Unknown upload type: {upload_info['type']}")
                return None
                
        except Exception as e:
            BBQTheme.error(f"Download and reassemble failed: {e}")
            return None

class FileWatcher:
    """File watcher for automatic QR code generation"""
    
    def __init__(self, file_path, output_path=None, qr_size=10):
        self.file_path = os.path.abspath(file_path)
        self.qr_size = qr_size
        
        # Generate output path if not provided
        if output_path:
            self.output_path = os.path.abspath(output_path)
        else:
            # Use the same directory as the watched file
            file_dir = os.path.dirname(self.file_path)
            file_name = os.path.splitext(os.path.basename(self.file_path))[0]
            self.output_path = os.path.join(file_dir, f"{file_name}_qr.png")
        
        self.qr_cooker = QRCooker(size=qr_size)
        self.last_modified = 0
        self.observer = None
        
        # Generate initial QR code
        self._generate_qr()
    
    def _generate_qr(self):
        """Generate QR code from file contents"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if content:
                BBQTheme.info(f"🔥 Updating QR code from: {self.file_path}")
                
                # Create QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=self.qr_size,
                    border=4,
                )
                
                qr.add_data(content)
                qr.make(fit=True)
                
                # Create and save image
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(self.output_path)
                
                # Update timestamp
                self.last_modified = os.path.getmtime(self.file_path)
                
                BBQTheme.success(f"QR code updated: {self.output_path}")
                BBQTheme.info(f"Content: {len(content)} characters")
            else:
                BBQTheme.error("File is empty, skipping QR generation")
                
        except Exception as e:
            BBQTheme.error(f"Failed to generate QR code: {e}")
    
    def start_watching(self):
        """Start watching the file for changes"""
        try:
            # Try to use watchdog first
            self.observer = Observer()
            event_handler = FileChangeHandler(self)
            
            # Watch the directory containing the file
            watch_dir = os.path.dirname(self.file_path)
            self.observer.schedule(event_handler, watch_dir, recursive=False)
            
            self.observer.start()
            
            BBQTheme.success(f"🔥 Started watching: {self.file_path}")
            BBQTheme.info(f"📱 QR codes will be saved to: {self.output_path}")
            BBQTheme.info(f"💨 Press Ctrl+C to stop watching...")
            
            while self.observer.is_alive():
                self.observer.join(1)
                
        except Exception as e:
            BBQTheme.error(f"Watchdog failed: {e}")
            BBQTheme.info("Falling back to polling method...")
            self._start_polling()
        except KeyboardInterrupt:
            self.stop_watching()
    
    def _start_polling(self):
        """Fallback polling method for file watching"""
        BBQTheme.success(f"🔥 Started polling: {self.file_path}")
        BBQTheme.info(f"📱 QR codes will be saved to: {self.output_path}")
        BBQTheme.info(f"💨 Press Ctrl+C to stop watching...")
        
        try:
            while True:
                try:
                    current_modified = os.path.getmtime(self.file_path)
                    if current_modified > self.last_modified:
                        time.sleep(0.1)  # Small delay to ensure file write is complete
                        self._generate_qr()
                except OSError:
                    # File might be temporarily unavailable
                    pass
                time.sleep(1)  # Check every second
        except KeyboardInterrupt:
            self.stop_watching()
    
    def stop_watching(self):
        """Stop watching the file"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        BBQTheme.info("🔥 Stopped watching file. Keep grilling!")

class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events"""
    
    def __init__(self, file_watcher):
        self.file_watcher = file_watcher
        super().__init__()
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and event.src_path == self.file_watcher.file_path:
            # Check if file was actually modified (avoid duplicate events)
            try:
                current_modified = os.path.getmtime(self.file_watcher.file_path)
                if current_modified > self.file_watcher.last_modified:
                    # Small delay to ensure file write is complete
                    time.sleep(0.1)
                    self.file_watcher._generate_qr()
            except OSError:
                # File might be temporarily unavailable during write
                pass

class QRCooker:
    """The main QR code cooking class"""
    
    def __init__(self, size=10, border=4):
        self.size = size
        self.border = border
    
    def cook_qr(self, data, save_file=False, copy_to_clipboard=False, prefix="qr"):
        """Cook (generate) a QR code from data"""
        BBQTheme.cooking()
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.size,
            border=self.border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Copy original data to clipboard if requested
        if copy_to_clipboard:
            try:
                pyperclip.copy(data)
                BBQTheme.success(f"Original data copied to clipboard! 📋")
            except Exception as e:
                BBQTheme.error(f"Failed to copy to clipboard: {e}")
        
        # Auto-generate filename if saving
        if save_file:
            try:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"bbqr_{prefix}_{timestamp}.png"
                img.save(filename)
                BBQTheme.success(f"QR code grilled and saved to: {filename}")
            except Exception as e:
                BBQTheme.error(f"Failed to save QR code: {e}")
        
        # Always display in terminal
        self.display_terminal_qr(qr)
        
        return img
    
    def display_terminal_qr(self, qr_code):
        """Display QR code in terminal using ASCII characters - compatible with dark/light modes"""
        print(f"\n{Fore.YELLOW}🔥 Your perfectly grilled QR code is ready! 🔥")
        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        matrix = qr_code.get_matrix()
        for row in matrix:
            line = ""
            for cell in row:
                # Use white blocks for QR code (visible on dark backgrounds)
                # and spaces for empty areas (visible on light backgrounds)
                line += f"{Fore.WHITE}██{Style.RESET_ALL}" if cell else "  "
            print(line)
        
        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

class BBQRCooker:
    """Main BBQR application class"""
    
    def __init__(self):
        self.qr_cooker = QRCooker()
        self.wifi_manager = WiFiManager()
    
    def handle_url(self, url, save_file=False, copy_to_clipboard=False):
        """Handle URL input"""
        BBQTheme.info(f"Grilling URL: {url}")
        return self.qr_cooker.cook_qr(url, save_file, copy_to_clipboard, "url")
    
    def handle_text(self, text, save_file=False, copy_to_clipboard=False):
        """Handle text input"""
        BBQTheme.info(f"Smoking text into QR code...")
        return self.qr_cooker.cook_qr(text, save_file, copy_to_clipboard, "text")
    
    def handle_image(self, image_path, save_file=False, copy_to_clipboard=False):
        """Handle image input - convert to base64"""
        try:
            with open(image_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
                BBQTheme.info(f"Converting image to base64 and grilling...")
                return self.qr_cooker.cook_qr(f"data:image/png;base64,{img_data}", save_file, copy_to_clipboard, "image")
        except Exception as e:
            BBQTheme.error(f"Failed to process image: {e}")
            return None
    
    def handle_clipboard(self, save_file=False, copy_to_clipboard=False):
        """Handle clipboard content"""
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content:
                BBQTheme.info("Found content in clipboard! Grilling it up...")
                return self.qr_cooker.cook_qr(clipboard_content, save_file, copy_to_clipboard, "clipboard")
            else:
                BBQTheme.error("Clipboard is empty! Nothing to grill.")
                return None
        except Exception as e:
            BBQTheme.error(f"Failed to access clipboard: {e}")
            return None
    
    def handle_wifi_menu(self, save_file=False, copy_to_clipboard=False):
        """Handle WiFi QR code generation with menu"""
        print(f"\n{Fore.MAGENTA}📶 WiFi QR Code Generator 📶")
        print(f"{Fore.CYAN}1. 🔥 Use saved WiFi profile")
        print(f"{Fore.CYAN}2. 🥩 Add new WiFi credentials")
        
        choice = input(f"\n{Fore.YELLOW}Choose your grilling method (1-2): ").strip()
        
        if choice == "1":
            return self.handle_saved_wifi(save_file, copy_to_clipboard)
        elif choice == "2":
            return self.handle_new_wifi(save_file, copy_to_clipboard)
        else:
            BBQTheme.error("Invalid choice! Please select 1 or 2.")
            return None
    
    def handle_saved_wifi(self, save_file=False, copy_to_clipboard=False):
        """Handle saved WiFi profiles"""
        profiles = self.wifi_manager.get_saved_wifi_profiles()
        
        if not profiles:
            BBQTheme.error("No saved WiFi profiles found!")
            BBQTheme.info("This might be due to permission issues or unsupported OS commands.")
            BBQTheme.info("Try using option 2 to enter WiFi credentials manually.")
            return None
        
        print(f"\n{Fore.CYAN}🔥 Saved WiFi Profiles:")
        for i, profile in enumerate(profiles, 1):
            print(f"{Fore.YELLOW}{i}. {profile}")
        
        try:
            choice = int(input(f"\n{Fore.YELLOW}Select WiFi profile (1-{len(profiles)}): ")) - 1
            if 0 <= choice < len(profiles):
                selected_profile = profiles[choice]
                password = self.wifi_manager.get_wifi_password(selected_profile)
                
                if password:
                    BBQTheme.info(f"Grilling WiFi QR code for: {selected_profile}")
                    wifi_string = self.wifi_manager.create_wifi_qr_string(
                        selected_profile, password)
                    return self.qr_cooker.cook_qr(wifi_string, save_file, copy_to_clipboard, "wifi")
                else:
                    BBQTheme.error(f"Could not retrieve password for {selected_profile}")
                    BBQTheme.info("Let's get the password manually...")
                    
                    print(f"\n{Fore.CYAN}Security Types:")
                    print("1. WPA/WPA2")
                    print("2. WEP") 
                    print("3. Open (No password)")
                    
                    security_choice = input(f"\n{Fore.YELLOW}Select security type (1-3): ").strip()
                    security_map = {"1": "WPA", "2": "WEP", "3": ""}
                    security_type = security_map.get(security_choice, "WPA")
                    
                    manual_password = ""
                    if security_type in ["WPA", "WEP"]:
                        manual_password = input(f"{Fore.YELLOW}Enter password for {selected_profile}: ").strip()
                    
                    BBQTheme.info(f"Grilling WiFi QR code for: {selected_profile}")
                    wifi_string = self.wifi_manager.create_wifi_qr_string(
                        selected_profile, manual_password, security_type)
                    return self.qr_cooker.cook_qr(wifi_string, save_file, copy_to_clipboard, "wifi")
            else:
                BBQTheme.error("Invalid selection!")
                return None
        except ValueError:
            BBQTheme.error("Please enter a valid number!")
            return None
    
    def handle_new_wifi(self, save_file=False, copy_to_clipboard=False):
        """Handle new WiFi credentials input"""
        print(f"\n{Fore.CYAN}🥩 Enter new WiFi credentials:")
        
        ssid = input(f"{Fore.YELLOW}WiFi Name (SSID): ").strip()
        if not ssid:
            BBQTheme.error("SSID cannot be empty!")
            return None
        
        print(f"\n{Fore.CYAN}Security Types:")
        print("1. WPA/WPA2")
        print("2. WEP") 
        print("3. Open (No password)")
        
        security_choice = input(f"\n{Fore.YELLOW}Select security type (1-3): ").strip()
        
        security_map = {"1": "WPA", "2": "WEP", "3": ""}
        security_type = security_map.get(security_choice, "WPA")
        
        password = ""
        if security_type in ["WPA", "WEP"]:
            password = input(f"{Fore.YELLOW}Password: ").strip()
        
        BBQTheme.info(f"Grilling WiFi QR code for: {ssid}")
        wifi_string = self.wifi_manager.create_wifi_qr_string(ssid, password, security_type)
        return self.qr_cooker.cook_qr(wifi_string, save_file, copy_to_clipboard, "wifi")
    
    def handle_upload(self, file_path, save_file=False, copy_to_clipboard=False, use_secret=True, expires_hours=None):
        """Handle file upload to 0x0.st and generate QR code"""
        if not os.path.exists(file_path):
            BBQTheme.error(f"File not found: {file_path}")
            return None
        
        if not os.path.isfile(file_path):
            BBQTheme.error(f"Path is not a file: {file_path}")
            return None
        
        try:
            # Upload the file (with chunking if necessary)
            upload_info = FileUploader.upload_file_chunked(file_path, use_secret, expires_hours)
            
            if not upload_info:
                BBQTheme.error("File upload failed!")
                return None
            
            # Create QR code data
            qr_data = f"BBQR_FILE:{json.dumps(upload_info, separators=(',', ':'))}"
            
            BBQTheme.success(f"🎉 File uploaded successfully!")
            BBQTheme.info(f"📁 Filename: {upload_info['filename']}")
            BBQTheme.info(f"📏 Size: {FileUploader.format_size(upload_info['size'])}")
            
            if upload_info['type'] == 'chunked':
                BBQTheme.info(f"📦 Chunks: {upload_info['chunks']}")
            
            BBQTheme.info("🔥 Generating QR code for file download...")
            
            # Generate QR code
            return self.qr_cooker.cook_qr(qr_data, save_file, copy_to_clipboard, "file_upload")
            
        except Exception as e:
            BBQTheme.error(f"File upload failed: {e}")
            return None
    
    def handle_upload_menu(self, save_file=False, copy_to_clipboard=False):
        """Handle file upload menu with options"""
        print(f"\n{Fore.MAGENTA}📤 File Upload to 0x0.st 📤")
        print(f"{Fore.CYAN}Upload files and generate QR codes for easy sharing!")
        print(f"{Fore.YELLOW}⏰ Files will be automatically removed after 30 days")
        print(f"{Fore.RED}ALL DATA IS STORED ON 0x0.st - PLEASE READ THE TOS AND PRIVACY POLICY BEFORE USING.")
        
        # Get file path input
        file_path = get_file_path(f"{Fore.YELLOW}Enter file path: ")
        
        if not file_path:
            BBQTheme.error("File path cannot be empty!")
            return None
        
        if not os.path.exists(file_path):
            BBQTheme.error(f"File not found: {file_path}")
            # Show some helpful suggestions
            dir_path = os.path.dirname(file_path)
            if os.path.exists(dir_path):
                BBQTheme.info(f"Directory exists: {dir_path}")
                try:
                    similar_files = [f for f in os.listdir(dir_path) 
                                   if os.path.basename(file_path).lower() in f.lower()]
                    if similar_files:
                        BBQTheme.info(f"Similar files found: {', '.join(similar_files[:5])}")
                except OSError:
                    pass
            return None
        
        if not os.path.isfile(file_path):
            BBQTheme.error(f"Path is not a file: {file_path}")
            return None
        
        # Display file info
        try:
            file_size = os.path.getsize(file_path)
            BBQTheme.info(f"📁 File: {os.path.basename(file_path)}")
            BBQTheme.info(f"📏 Size: {FileUploader.format_size(file_size)}")
        except OSError:
            pass
        
        # Upload and generate QR code with 30-day expiration
        return self.handle_upload(file_path, save_file, copy_to_clipboard, use_secret=True, expires_hours=720)
    
    def handle_piped_input(self, save_file=False, copy_to_clipboard=False):
        """Handle piped input from stdin"""
        if not sys.stdin.isatty():  # Check if data is piped
            piped_data = sys.stdin.read().strip()
            if piped_data:
                BBQTheme.info("Found piped data! Grilling it up...")
                return self.qr_cooker.cook_qr(piped_data, save_file, copy_to_clipboard, "piped")
        return None
    
    def handle_watch(self, file_path, output_path=None, qr_size=10):
        """Handle file watching for automatic QR code generation"""
        if not os.path.exists(file_path):
            BBQTheme.error(f"File not found: {file_path}")
            return None
        
        if not os.path.isfile(file_path):
            BBQTheme.error(f"Path is not a file: {file_path}")
            return None
        
        try:
            watcher = FileWatcher(file_path, output_path, qr_size)
            watcher.start_watching()
        except Exception as e:
            BBQTheme.error(f"Failed to start file watcher: {e}")
            return None
    
    def handle_multi(self, file_path, qr_size=10):
        """Handle multiple QR code generation from file"""
        if not os.path.exists(file_path):
            BBQTheme.error(f"File not found: {file_path}")
            return None
        
        if not os.path.isfile(file_path):
            BBQTheme.error(f"Path is not a file: {file_path}")
            return None
        
        try:
            # Create qrcodes directory
            qrcodes_dir = "qrcodes"
            os.makedirs(qrcodes_dir, exist_ok=True)
            
            BBQTheme.info(f"🔥 Processing multi-QR generation from: {file_path}")
            BBQTheme.info(f"📁 QR codes will be saved to: {qrcodes_dir}/")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                BBQTheme.error("File is empty!")
                return None
            
            successful_count = 0
            total_count = 0
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                total_count += 1
                
                try:
                    # Create QR code without terminal display
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=qr_size,
                        border=4,
                    )
                    
                    qr.add_data(line)
                    qr.make(fit=True)
                    
                    # Create and save image
                    img = qr.make_image(fill_color="black", back_color="white")
                    output_path = os.path.join(qrcodes_dir, f"{line_num}.png")
                    img.save(output_path)
                    
                    successful_count += 1
                    
                    # Show preview of content (truncated for long lines)
                    preview = line[:50] + "..." if len(line) > 50 else line
                    BBQTheme.success(f"#{line_num}: {output_path} - {preview}")
                    
                except Exception as e:
                    BBQTheme.error(f"#{line_num}: Failed to generate QR code - {e}")
            
            # Summary
            print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            BBQTheme.success(f"Multi-QR generation complete!")
            BBQTheme.info(f"📊 Successfully generated: {successful_count}/{total_count} QR codes")
            BBQTheme.info(f"📁 All QR codes saved to: {os.path.abspath(qrcodes_dir)}/")
            print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            return successful_count
            
        except Exception as e:
            BBQTheme.error(f"Failed to process multi-QR generation: {e}")
            return None
    
    def handle_read(self, image_path):
        """Handle QR code reading from image file"""
        if not os.path.exists(image_path):
            BBQTheme.error(f"Image file not found: {image_path}")
            return None
        
        if not os.path.isfile(image_path):
            BBQTheme.error(f"Path is not a file: {image_path}")
            return None
        
        # Check if file is an image
        valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        file_ext = os.path.splitext(image_path.lower())[1]
        if file_ext not in valid_extensions:
            BBQTheme.error(f"Unsupported image format: {file_ext}")
            BBQTheme.info("Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF")
            return None
        
        BBQTheme.info(f"🔍 Reading QR code from: {image_path}")
        
        # Decode the QR code
        qr_data, error = QRReader.decode_qr(image_path)
        
        if error:
            BBQTheme.error(error)
            return None
        
        if not qr_data:
            BBQTheme.error("No QR code data found")
            return None
        
        print(f"{Fore.GREEN}✅ QR Code Successfully Decoded!")
        
        # Determine content type and handle accordingly
        if QRReader.handle_wifi_qr(qr_data):
            return "wifi"
        elif QRReader.handle_file_upload_qr(qr_data):
            return "file_upload"
        elif QRReader.handle_image_qr(qr_data):
            return "image"
        else:
            QRReader.handle_text_qr(qr_data)
            return "text"

def show_license():
    """Display license information"""
    with open("LICENSE", "r", encoding="utf-8") as license_file:
        license_text = license_file.read()
    print(f"\n{Fore.YELLOW}🔥 BBQR License Information 🔥")
    print(license_text)

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="🔥 BBQR (Barbequer) - Grill your data into QR codes! 🔥",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bbqr --url https://github.com
  bbqr --text "Hello World!"
  bbqr --image photo.jpg
  bbqr --clipboard
  bbqr --wifi
  bbqr --file document.pdf
  bbqr --file large_file.zip
  bbqr --text "Hello World!" --save
  bbqr --url https://github.com --copy
  bbqr --text "Hello World!" --save --copy
  bbqr --watch journal.txt
  bbqr --watch journal.txt --output /path/to/qr_codes/journal_qr.png
  bbqr --watch notes.md --size 15
  bbqr --multi urls.txt
  bbqr --multi data.txt --size 12
  bbqr --read qrcode.png
  bbqr -r wifi_qr.png
  bbqr --license
  echo "piped data" | bbqr --save
  echo "piped data" | bbqr --copy
        """
    )
    
    parser.add_argument('--url', '-u', help='Generate QR code from URL')
    parser.add_argument('--text', '-t', help='Generate QR code from text')
    parser.add_argument('--image', '-i', help='Generate QR code from image file')
    parser.add_argument('--clipboard', '-c', action='store_true', 
                       help='Generate QR code from clipboard content')
    parser.add_argument('--wifi', '-w', action='store_true',
                       help='Generate WiFi QR code')
    parser.add_argument('--file', '-f', help='Upload file to 0x0.st and generate QR code for download')
    parser.add_argument('--watch', help='Watch a file for changes and auto-generate QR codes')
    parser.add_argument('--multi', help='Generate QR codes from multiple lines in a file')
    parser.add_argument('--read', '-r', help='Read and decode QR code from image file')
    parser.add_argument('--output', '-o', help='Output path for watch mode (default: same directory as watched file)')
    parser.add_argument('--size', '-s', type=int, default=10,
                       help='QR code size (default: 10)')
    parser.add_argument('--save', action='store_true', 
                       help='Save QR code as PNG file')
    parser.add_argument('--copy', action='store_true',
                       help='Copy original data to clipboard')
    parser.add_argument('--license', action='store_true',
                       help='Show license information and exit')
    
    args = parser.parse_args()
    
    # Handle license display first
    if args.license:
        show_license()
        return
    
    BBQTheme.welcome()
    
    cooker = BBQRCooker()
    cooker.qr_cooker.size = args.size
    
    # Check for piped input first
    piped_result = cooker.handle_piped_input(args.save, args.copy)
    if piped_result:
        return
    
    # Handle different input types
    if args.url:
        cooker.handle_url(args.url, args.save, args.copy)
    elif args.text:
        cooker.handle_text(args.text, args.save, args.copy)
    elif args.image:
        if os.path.exists(args.image):
            cooker.handle_image(args.image, args.save, args.copy)
        else:
            BBQTheme.error(f"Image file not found: {args.image}")
    elif args.clipboard:
        cooker.handle_clipboard(args.save, args.copy)
    elif args.wifi:
        cooker.handle_wifi_menu(args.save, args.copy)
    elif args.file:
        if os.path.exists(args.file):
            cooker.handle_upload(args.file, args.save, args.copy, use_secret=True, expires_hours=720)  # 30 days
        else:
            BBQTheme.error(f"File not found: {args.file}")
    elif args.watch:
        cooker.handle_watch(args.watch, args.output, args.size)
    elif args.multi:
        cooker.handle_multi(args.multi, args.size)
    elif args.read:
        cooker.handle_read(args.read)
    else:
        # Interactive mode
        print(f"{Fore.MAGENTA}🍖 Interactive Mode - What would you like to grill?")
        print(f"{Fore.CYAN}1. 🌐 URL")
        print(f"{Fore.CYAN}2. 📝 Text")
        print(f"{Fore.CYAN}3. 🖼️  Image")
        print(f"{Fore.CYAN}4. 📋 Clipboard")
        print(f"{Fore.CYAN}5. 🛜  WiFi")
        print(f"{Fore.CYAN}6. ⬆️  Upload File")
        print(f"{Fore.CYAN}7. 👀 Watch File")
        print(f"{Fore.CYAN}8. 📂 Multi QR from File")
        print(f"{Fore.CYAN}9. 🔍 Read QR Code")
        
        choice = input(f"\n{Fore.YELLOW}Select your grilling option (1-9): ").strip()
        
        if choice == "1":
            url = input(f"{Fore.YELLOW}Enter URL: ").strip()
            if url:
                cooker.handle_url(url, args.save, args.copy)
        elif choice == "2":
            text = input(f"{Fore.YELLOW}Enter text: ").strip()
            if text:
                cooker.handle_text(text, args.save, args.copy)
        elif choice == "3":
            image_path = get_file_path(f"{Fore.YELLOW}Enter image path: ")
            if image_path and os.path.exists(image_path):
                cooker.handle_image(image_path, args.save, args.copy)
            else:
                BBQTheme.error("Image file not found!")
        elif choice == "4":
            cooker.handle_clipboard(args.save, args.copy)
        elif choice == "5":
            cooker.handle_wifi_menu(args.save, args.copy)
        elif choice == "6":
            cooker.handle_upload_menu(args.save, args.copy)
        elif choice == "7":
            file_path = get_file_path(f"{Fore.YELLOW}Enter file path to watch: ")
            if file_path:
                output_path = get_file_path(f"{Fore.YELLOW}Enter output path (press Enter for default): ", allow_empty=True)
                output_path = output_path if output_path else None
                cooker.handle_watch(file_path, output_path, args.size)
            else:
                BBQTheme.error("File path cannot be empty!")
        elif choice == "8":
            file_path = get_file_path(f"{Fore.YELLOW}Enter file path with multiple lines: ")
            if file_path:
                cooker.handle_multi(file_path, args.size)
                cooker.handle_multi(file_path, args.size)
            else:
                BBQTheme.error("File path cannot be empty!")
        elif choice == "9":
            image_path = get_file_path(f"{Fore.YELLOW}Enter QR code image path: ")
            if image_path:
                cooker.handle_read(image_path)
            else:
                BBQTheme.error("Image path cannot be empty!")
        else:
            BBQTheme.error("Invalid choice!")
    
    print(f"\n{Fore.GREEN}🔥 Thanks for using BBQR! Keep grilling! 🔥")

if __name__ == "__main__":
    main()
