import os
import subprocess
import re
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='CSES_Offline')

# تنظیمات
JUDGE_SCRIPT = "judge.py"


def strip_ansi_codes(text):
    """حذف کدهای رنگی ترمینال برای نمایش تمیز در مرورگر"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


@app.route('/')
def index():
    return send_from_directory('CSES_Offline', 'index.html')


# سرو کردن تمام فایل‌های استاتیک (HTML, CSS, JS)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('CSES_Offline', path)


@app.route('/api/submit', methods=['POST'])
def handle_submit():
    data = request.json
    problem_id = data.get('id')
    code = data.get('code')

    if not problem_id or not code:
        return jsonify({'output': 'Missing ID or Code', 'success': False}), 400

    # 1. ذخیره کد در یک فایل موقت
    solution_filename = f"temp_sol_{problem_id}.cpp"
    with open(solution_filename, 'w') as f:
        f.write(code)

    # 2. اجرای judge.py
    # ما خروجی استاندارد را کپچر می‌کنیم
    try:
        # اجرای دستور: python3 judge.py <ID> <FILE>
        # unbuffered (-u) برای اطمینان از خروجی درست
        cmd = ["python3", "-u", JUDGE_SCRIPT, str(problem_id), solution_filename]

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        raw_output = process.stdout + process.stderr
        clean_output = strip_ansi_codes(raw_output)

        # تشخیص موفقیت (ساده)
        is_success = "ALL TESTS PASSED" in clean_output

        # پاک کردن فایل موقت
        if os.path.exists(solution_filename):
            os.remove(solution_filename)

        return jsonify({
            'output': clean_output,
            'success': is_success
        })

    except Exception as e:
        return jsonify({'output': f"Server Error: {str(e)}", 'success': False}), 500


if __name__ == '__main__':
    print("🚀 CSES Offline Server running...")
    # تغییر مهم: host='0.0.0.0' برای دسترسی از بیرون کانتینر ضروری است
    app.run(host='0.0.0.0', port=5000, debug=True)