# 🏆 CSES Offline Judge & Mirror

**A complete, offline environment for solving and judging CSES problems locally.**

This project allows you to download the entire [CSES](https://cses.fi) problem set (including test cases), run a local judging server, and submit C++ solutions without an internet connection. It mimics the real CSES experience using a local Python backend and Docker.

---

## ✨ Features

* **📥 Smart Scraper:** Securely downloads problems, descriptions, and test cases using your session cookie.
* **⚙️ Auto-Processor:** Extracts tests, cleans up HTML (removes online-only features), and injects a submission UI.
* **⚖️ Local Judge:** Compiles (g++) and runs your code against real test cases with strict time limit enforcement.
* **🐳 Dockerized:** Runs in an isolated, consistent Linux environment (just like the real judge servers).
* **⚡️ Fast & Lightweight:** Powered by a simple Flask backend and vanilla JavaScript.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/AliRajabian/CSES-Offline-Judge.git
cd CSES-Offline-Judge

```

### 2. Download Problems (The Scraper)

First, you need to download the content.

> **⚠️ Important:** You need your `PHPSESSID` cookie from cses.fi to download test cases.
> 1. Log in to cses.fi.
> 2. Open Developer Tools (F12) -> Application -> Cookies.
> 3. Copy the value of `PHPSESSID`.
> 
> 

Run the scraper:

```bash
python3 scraper.py

```

*Enter your session ID when prompted. The script will save problems to the `CSES_Offline/` directory.*

### 3. Prepare Environment (The Processor)

Once downloaded, run this script to extract ZIP files, fix links, and add the "Submit" button to the offline pages:

```bash
python3 processor.py

```

### 4. Run the Server

You have two options to run the judge:

#### Option A: Using Docker (Recommended) 🐳

This ensures your code runs in a standard Linux environment.

```bash
docker-compose up --build

```

#### Option B: Manual Run (Python) 🐍

If you don't use Docker, ensure you have **Python 3.9+** and **g++** installed.

```bash
pip install -r requirements.txt
python3 server.py

```

### 5. Start Coding!

Open your browser and navigate to:
👉 **http://localhost:8080** (if using Docker)
👉 **http://localhost:5000** (if using manual run)

Browse a problem, write your C++ solution in the text area, and click **"Run & Judge"**.

---

## 📂 Project Structure

* `scraper.py`: Handles downloading raw HTML and test data from CSES.
* `processor.py`: Post-processing script to extract tests, clean UI, and fix navigation.
* `server.py`: Flask web server to serve the offline site and handle API requests.
* `judge.py`: The core logic that compiles C++ code and validates output against test cases.
* `Dockerfile` & `docker-compose.yml`: Configuration for containerizing the application.
* `CSES_Offline/`: (Generated) Contains the downloaded problem set. **Ignored by Git** to respect copyright.

---

## ⚠️ Disclaimer & Copyright

This tool is created for **personal educational use and offline practice only**.

The problem statements, test data, and website assets are the intellectual property of **CSES (cses.fi)**.

* Do not redistribute the downloaded `CSES_Offline` folder publicly.
* Do not use this tool to spam the CSES servers.

---

Made with ❤️ by [Ali Rajabian](https://www.google.com/search?q=https://github.com/AliRajabian)

