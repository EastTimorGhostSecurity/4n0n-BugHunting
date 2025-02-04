import requests
import paramiko
import logging
import urllib.parse
import time
import sys
import signal

# Setup logging
logging.basicConfig(filename='vulnerability_scan.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_payloads(file_path):
    """Load payloads from a file."""
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"[ERROR] File {file_path} not found.")
        return []

def check_sql_injection(url, payloads):
    print(f"Checking for SQL Injection vulnerabilities on {url}...")
    for payload in payloads:
        test_url = f"{url}?id={urllib.parse.quote(payload)}"
        try:
            response = requests.get(test_url)
            if "error" in response.text.lower() or "mysql" in response.text.lower():
                print(f"[!] Potential SQL Injection vulnerability found with payload: {payload}")
                logging.info(f"SQL Injection vulnerability found: {test_url}")
            else:
                print(f"[ ] No vulnerability found with payload: {payload}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error making request: {e}")

def check_ssh_vulnerability(host, port=22, timeout=5, retries=3):
    common_usernames = load_payloads('usernames.txt')
    common_passwords = load_payloads('passwords.txt')
    
    if not common_usernames or not common_passwords:
        print("[ERROR] Usernames or passwords file is empty or not found.")
        return

    print(f"Checking for SSH vulnerabilities on {host}...")
    
    for username in common_usernames:
        for password in common_passwords:
            for attempt in range(retries):
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(host, port=port, username=username, password=password, timeout=timeout)
                    print(f"[!] SSH Vulnerability found! Username: {username}, Password: {password}")
                    logging.info(f"SSH Vulnerability found: Username: {username}, Password: {password}")
                    client.close()
                    return  # Stop after finding the first vulnerability
                except paramiko.AuthenticationException:
                    print(f"[ ] Failed login for Username: {username}, Password: {password} (Attempt {attempt + 1})")
                except Exception as e:
                    print(f"[ERROR] Error connecting to {host}: {e}")
                    break  # Stop trying if there's a connection error

def check_xss_vulnerability(url, payloads):
    print(f"Checking for XSS vulnerabilities on {url}...")
    for payload in payloads:
        test_url = f"{url}?search={urllib.parse.quote(payload)}"
        try:
            response = requests.get(test_url)
            if payload in response.text:
                print(f"[!] Potential XSS vulnerability found with payload: {payload}")
                logging.info(f"XSS vulnerability found: {test_url}")
            else:
                print(f"[ ] No vulnerability found with payload: {payload}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error making request: {e}")

def check_csrf_vulnerability(url, payloads):
    print(f"Checking for CSRF vulnerabilities on {url}...")
    for payload in payloads:
        try:
            response = requests.post(url, data={payload.split('=')[0]: payload.split('=')[1]})
            if response.status_code == 200:
                print(f"[!] CSRF vulnerability potentially exploitable with payload: {payload}")
                logging.info(f"CSRF vulnerability found: {url} with payload: {payload}")
            else:
                print(f"[ ] No vulnerability found with payload: {payload}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error making request: {e}")

# Banner with red, yellow, and white colors
banner = """
\033[1;33m███████╗ █████╗ ███████╗████████╗    ████████╗██╗███╗   ███╗ ██████╗ ██████╗      ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗███████╗███████╗ ██████╗
\033[1;33m██╔════╝██╔══██╗██╔════╝╚══██╔══╝    ╚══██╔══╝██║████╗ ████║██╔═══██╗██╔══██╗    ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔════╝
\033[1;37m█████╗  ███████║███████╗   ██║          ██║   ██║██╔████╔██║██║   ██║██████╔╝    ██║  ███╗███████║██║   ██║███████╗   ██║   ███████╗█████╗  ██║     
\033[1;37m██╔══╝  ██╔══██║╚════██║   ██║          ██║   ██║██║╚██╔╝██║██║   ██║██╔══██╗    ██║   ██║██╔══██║██║   ██║╚════██║   ██║   ╚════██║██╔══╝  ██║     
\033[1;31m███████╗██║  ██║███████║   ██║          ██║   ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║    ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ███████║███████╗╚██████╗
\033[1;31m╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝          ╚═╝   ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚══════╝ ╚═════╝
\033[1;37m
"""

def animated_print(text, delay=0.02):
    """Print text with a typing effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Move to the next line after the message

def signal_handler(sig, frame):
    # Handle Ctrl+C
    print("\n", end="")  # Move to the next line
    animated_print("THANK YOU FOR USING THE TOOLS")
    sys.exit(0)

def main():
    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Print the banner
    animated_print(banner)
    
    # Center the version text
    version_text = "Code by EAST TIMOR GHOST SECURITY (Mr.Y) version: 1.0"
    banner_lines = banner.splitlines()
    banner_width = max(len(line) for line in banner_lines)
    centered_text = version_text.center(banner_width)
    animated_print(centered_text)

    # Menu options
    print("=============SELECT YOUR CHOICE==============:")
    print("[1] Check for SQL Injection vulnerabilities")
    print("[2] Check for SSH vulnerabilities")
    print("[3] Check for XSS vulnerabilities")
    print("[4] Check for CSRF vulnerabilities")
    
    choice = input("Enter your choice: ")
    
    if choice == '1':
        target_url = input("Enter the URL to test for SQL Injection: ")
        payload_file = input("Enter the path to the SQL payload file (e.g., sql_payloads.txt): ")
        payloads = load_payloads(payload_file)
        if payloads:
            check_sql_injection(target_url, payloads)
        else:
            print("[ERROR] No payloads loaded. Please check your payload file.")
    elif choice == '2':
        target_host = input("Enter the SSH host to test: ")
        check_ssh_vulnerability(target_host)
    elif choice == '3':
        target_url = input("Enter the URL to test for XSS: ")
        payload_file = input("Enter the path to the XSS payload file (e.g., xss_payloads.txt): ")
        payloads = load_payloads(payload_file)
        if payloads:
            check_xss_vulnerability(target_url, payloads)
        else:
            print("[ERROR] No payloads loaded. Please check your payload file.")
    elif choice == '4':
        target_url = input("Enter the URL to test for CSRF: ")
        payload_file = input("Enter the path to the CSRF payload file (e.g., csrf_payloads.txt): ")
        payloads = load_payloads(payload_file)
        if payloads:
            check_csrf_vulnerability(target_url, payloads)
        else:
            print("[ERROR] No payloads loaded. Please check your payload file.")
    else:
        print("[ERROR] Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
