import os
import time
import requests
from bs4 import BeautifulSoup

# تنظیمات
BASE_URL = "https://cses.fi"
PROBLEMSET_URL = "https://cses.fi/problemset/"
OUTPUT_DIR = "CSES_Offline"


def get_headers(session_id):
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"PHPSESSID={session_id}"
    }


def save_file(path, content, mode='w'):
    try:
        with open(path, mode) as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error saving {path}: {e}")


def download_problem(session_id, problem_url, problem_id, problem_name):
    headers = get_headers(session_id)
    folder_name = f"{problem_id} - {problem_name}"
    folder_path = os.path.join(OUTPUT_DIR, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    print(f"🔹 Processing: {folder_name}...")

    # 1. دانلود HTML
    try:
        response = requests.get(problem_url, headers=headers)
        if response.status_code == 200:
            save_file(os.path.join(folder_path, "problem.html"), response.text, 'w')
    except Exception as e:
        print(f"   ❌ Error fetching problem text: {e}")

    # 2. دانلود تست‌ها (POST Request)
    tests_url = f"{BASE_URL}/problemset/tests/{problem_id}/"
    try:
        session = requests.Session()
        test_page_resp = requests.get(tests_url, headers=headers)
        if test_page_resp.status_code == 200:
            soup = BeautifulSoup(test_page_resp.content, "html.parser")
            csrf_input = soup.find("input", {"name": "csrf_token"})

            if csrf_input:
                csrf_token = csrf_input.get("value")
                payload = {"csrf_token": csrf_token, "download": "Download"}
                print(f"   ⬇️ Downloading tests...")
                zip_resp = requests.post(tests_url, headers=headers, data=payload)
                if zip_resp.status_code == 200 and "application/zip" in zip_resp.headers.get("Content-Type", ""):
                    save_file(os.path.join(folder_path, "tests.zip"), zip_resp.content, 'wb')
                    print("   ✅ Tests downloaded.")
                else:
                    print("   ⚠️ Download failed or not a zip.")
            else:
                print("   🔸 CSRF Token not found (Login might be required).")
    except Exception as e:
        print(f"   ❌ Error fetching tests: {e}")


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("👋 Welcome to CSES Scraper!")
    print("⚠️  You need your PHPSESSID from your browser cookies to download test cases.")
    session_id = input("👉 Enter PHPSESSID: ").strip()

    if not session_id:
        print("❌ No Session ID provided. Exiting.")
        return

    print("🚀 Connecting to CSES...")
    try:
        response = requests.get(PROBLEMSET_URL, headers=get_headers(session_id))
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    tasks = soup.select(".task a")
    print(f"📋 Found {len(tasks)} problems. Starting download...")

    for task in tasks:
        href = task.get('href')
        if not href: continue
        parts = href.strip("/").split("/")
        if len(parts) >= 3:
            problem_id = parts[-1]
            problem_name = task.get_text(strip=True)
            full_url = f"{BASE_URL}{href}"
            download_problem(session_id, full_url, problem_id, problem_name)
            time.sleep(1)

    print("\n🎉 Download Complete! Now run 'python3 processor.py' to extract and setup.")


if __name__ == "__main__":
    main()