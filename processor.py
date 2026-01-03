import os
import re
import requests
import zipfile
import shutil
from bs4 import BeautifulSoup

ROOT_DIR = "CSES_Offline"
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

# --- 1. تنظیمات HTML ---
SUBMIT_HTML = """
<div id="local-submit-area" style="margin-top: 40px; padding: 20px; background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px;">
    <h3>💻 Local Submit</h3>
    <textarea id="source-code" placeholder="#include <iostream>..." style="width: 100%; height: 200px; font-family: monospace; padding: 10px; border: 1px solid #ccc; border-radius: 4px;"></textarea>
    <br>
    <button onclick="submitCode()" style="margin-top: 10px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">Run & Judge</button>
    <div id="judge-result" style="margin-top: 20px; white-space: pre-wrap; font-family: monospace; background: #222; color: #fff; padding: 15px; border-radius: 4px; display: none;"></div>
</div>
<script>
async function submitCode() {
    const code = document.getElementById('source-code').value;
    const resultDiv = document.getElementById('judge-result');
    const pathParts = window.location.pathname.split('/');
    let problemId = null;
    for (let part of pathParts) {
        let decoded = decodeURIComponent(part);
        if (decoded.match(/^\d+ - /)) { problemId = decoded.split(' - ')[0]; break; }
    }
    if (!code) { alert("Please write some code!"); return; }
    if (!problemId) { alert("Could not detect Problem ID."); return; }
    resultDiv.style.display = 'block'; resultDiv.innerHTML = "⏳ Running...";
    try {
        const response = await fetch('/api/submit', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: problemId, code: code })
        });
        const data = await response.json();
        resultDiv.innerText = data.output;
        resultDiv.style.borderLeft = data.success ? "5px solid #28a745" : "5px solid #dc3545";
    } catch (err) { resultDiv.innerText = "Error: " + err; }
}
</script>
"""


def download_assets():
    print("📦 Downloading Assets (CSS/JS)...")
    base_url = "https://cses.fi"
    files = ["/cses.css", "/cses-dark.css", "/logo.png", "/ui.js",
             "/lib/fontawesome/css/all.min.css", "/lib/katex/katex.min.css",
             "/lib/katex/katex.min.js", "/lib/katex/contrib/copy-tex.min.js",
             "/lib/google-code-prettify/run_prettify.js"]
    if not os.path.exists(ASSETS_DIR): os.makedirs(ASSETS_DIR)
    for path in files:
        local_path = os.path.join(ASSETS_DIR, path.lstrip('/'))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        try:
            r = requests.get(base_url + path)
            if r.status_code == 200:
                with open(local_path, 'wb') as f: f.write(r.content)
        except:
            pass


def process_problem(folder_path, problem_id, problem_map):
    # 1. Extract Tests
    zip_path = os.path.join(folder_path, "tests.zip")
    tests_dir = os.path.join(folder_path, "tests")
    if os.path.exists(zip_path):
        if not os.path.exists(tests_dir):
            try:
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extractall(tests_dir)
            except:
                pass
        os.remove(zip_path)  # Cleanup Zip

    # 2. Patch HTML
    html_path = os.path.join(folder_path, "problem.html")
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Clean UI
        for x in soup.find_all(class_=['account', 'task-score']): x.decompose()
        controls = soup.find('div', class_='controls')
        if controls: controls.decompose()

        # Remove Tabs
        nav_ul = soup.select_one('.title-block .nav')
        if nav_ul:
            for li in nav_ul.find_all('li'):
                if any(x in li.find('a').get('href', '') for x in
                       ['submit', 'view', 'model', 'stats', 'queue', 'tests']):
                    li.decompose()

        # Fix Links (Assets & Navigation)
        str_soup = str(soup)
        str_soup = re.sub(r'(\.css|\.png|\.js)\?\d+', r'\1', str_soup)
        replacements = [
            ('href="/cses.css"', 'href="../assets/cses.css"'),
            ('href="/cses-dark.css"', 'href="../assets/cses-dark.css"'),
            ('src="/logo.png"', 'src="../assets/logo.png"'),
            ('src="/ui.js"', 'src="../assets/ui.js"'),
            ('href="/lib/', 'href="../assets/lib/'),
            ('src="/lib/', 'src="../assets/lib/'),
            ('href="/"', 'href="../index.html"')
        ]
        for old, new in replacements: str_soup = str_soup.replace(old, new)

        # Inject Submit UI
        if "local-submit-area" not in str_soup:
            content_div_end = str_soup.find('</div>', str_soup.find('class="content"'))
            # Simple string injection is safer than BS4 append sometimes
            soup = BeautifulSoup(str_soup, 'html.parser')
            content_div = soup.find('div', class_='content')
            if content_div: content_div.append(BeautifulSoup(SUBMIT_HTML, 'html.parser'))
            str_soup = str(soup)

        # Fix Problem Links
        def replace_link(match):
            tid = match.group(1)
            return f'href="../{problem_map.get(tid, tid)}/problem.html"' if tid in problem_map else match.group(0)

        str_soup = re.sub(r'href="/problemset/task/(\d+)/?"', replace_link, str_soup)

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str_soup)


def generate_index(problem_map):
    sorted_probs = sorted(problem_map.items(), key=lambda x: int(x[0]))
    html = """<html><head><meta charset='UTF-8'><title>CSES Offline</title>
    <style>body{font-family:sans-serif;max-width:800px;margin:40px auto;padding:20px;background:#f4f4f4}
    a{text-decoration:none;color:#007bff;display:block;padding:10px;background:#fff;margin-bottom:5px;border-radius:4px;}
    a:hover{background:#eee}</style></head><body><h1>CSES Offline Problems</h1>"""
    for pid, folder in sorted_probs:
        html += f'<a href="{folder}/problem.html"><b>{pid}</b> - {folder.replace(pid + " - ", "")}</a>'
    html += "</body></html>"
    with open(os.path.join(ROOT_DIR, "index.html"), 'w', encoding='utf-8') as f: f.write(html)


def main():
    if not os.path.exists(ROOT_DIR):
        print(f"❌ '{ROOT_DIR}' not found. Run scraper.py first.")
        return

    download_assets()

    # Create Map
    problem_map = {}
    for item in os.listdir(ROOT_DIR):
        if " - " in item and item.split(" - ")[0].isdigit():
            problem_map[item.split(" - ")[0]] = item

    print(f"🔧 Processing {len(problem_map)} problems...")
    for pid, folder in problem_map.items():
        process_problem(os.path.join(ROOT_DIR, folder), pid, problem_map)

    generate_index(problem_map)
    print("🎉 All Done! Environment is ready.")


if __name__ == "__main__":
    main()