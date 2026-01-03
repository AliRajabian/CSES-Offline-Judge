import os
import sys
import subprocess
import time
import glob
import re

# ============================
# تنظیمات سیستم جاج
# ============================
ROOT_DIR = "CSES_Offline"
DEFAULT_TIME_LIMIT = 1.0  # ثانیه (اکثر سوالات CSES یک ثانیه هستند)
COMPILER_CMD = ["g++", "-std=c++17", "-O2", "-Wall"]  # فلگ‌های استاندارد المپیاد


# رنگ‌ها برای خروجی ترمینال
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def compile_code(cpp_file):
    """کد C++ را کامپایل می‌کند و آدرس فایل اجرایی را برمی‌گرداند"""
    if not os.path.exists(cpp_file):
        print(f"{Colors.FAIL}❌ Error: File '{cpp_file}' not found.{Colors.ENDC}")
        sys.exit(1)

    exe_file = cpp_file.replace(".cpp", "")
    # اگر ویندوز بود باید .exe اضافه می‌شد، اما برای مک نیازی نیست

    print(f"{Colors.OKBLUE}🔨 Compiling {cpp_file}...{Colors.ENDC}")

    cmd = COMPILER_CMD + [cpp_file, "-o", exe_file]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{Colors.FAIL}❌ Compilation Error:{Colors.ENDC}")
            print(result.stderr)
            return None
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error invoking g++: {e}{Colors.ENDC}")
        return None

    return exe_file


def find_problem_path(problem_id):
    """پوشه سوال را بر اساس ID پیدا می‌کند"""
    if not os.path.exists(ROOT_DIR):
        print(f"{Colors.FAIL}❌ Error: Directory '{ROOT_DIR}' not found.{Colors.ENDC}")
        sys.exit(1)

    for item in os.listdir(ROOT_DIR):
        # بررسی می‌کنیم پوشه با ID شروع شود (مثلا 1068)
        if item.startswith(str(problem_id)) and os.path.isdir(os.path.join(ROOT_DIR, item)):
            return os.path.join(ROOT_DIR, item)
    return None


def natural_sort_key(s):
    """برای مرتب‌سازی درست فایل‌ها (که 10 بعد از 2 نیاید)"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]


def run_tests(problem_id, cpp_file):
    problem_path = find_problem_path(problem_id)
    if not problem_path:
        print(f"{Colors.FAIL}❌ Problem ID {problem_id} not found locally.{Colors.ENDC}")
        return

    tests_path = os.path.join(problem_path, "tests")
    if not os.path.exists(tests_path):
        print(f"{Colors.FAIL}❌ Tests folder not found. Run extract_tests.py first.{Colors.ENDC}")
        return

    # کامپایل کردن کد
    exe_file = compile_code(cpp_file)
    if not exe_file:
        return

    print(f"{Colors.HEADER}🚀 Running Judge on Problem: {os.path.basename(problem_path)}{Colors.ENDC}")
    print(f"Time Limit: {DEFAULT_TIME_LIMIT}s")
    print("-" * 50)

    # پیدا کردن فایل‌های ورودی
    # در CSES فایل‌های ورودی معمولا پسوند ندارند یا .in هستند
    # فایل‌های خروجی حتما .out هستند
    all_files = os.listdir(tests_path)
    input_files = [f for f in all_files if not f.endswith(".out") and not f.startswith(".")]
    input_files.sort(key=natural_sort_key)

    ac_count = 0
    total_count = len(input_files)

    # اجرای تست‌ها
    for test_in in input_files:
        in_path = os.path.join(tests_path, test_in)

        # پیدا کردن فایل خروجی متناظر
        expected_out_name = f"{test_in}.out"
        out_path = os.path.join(tests_path, expected_out_name)

        if not os.path.exists(out_path):
            # گاهی اوقات نام‌گذاری متفاوت است، مثلا input.in -> input.out
            if test_in.endswith(".in"):
                out_path = os.path.join(tests_path, test_in.replace(".in", ".out"))

            if not os.path.exists(out_path):
                print(f"{Colors.WARNING}⚠️ Skipping test {test_in}: No .out file found.{Colors.ENDC}")
                total_count -= 1
                continue

        # خواندن ورودی و خروجی مورد انتظار
        with open(out_path, 'r') as f:
            expected_output = f.read().strip()

        verdict = ""
        duration = 0.0

        try:
            with open(in_path, 'r') as infile:
                start_time = time.time()

                # اجرای برنامه کاربر
                process = subprocess.run(
                    [f"./{exe_file}"],
                    stdin=infile,
                    capture_output=True,
                    text=True,
                    timeout=DEFAULT_TIME_LIMIT
                )

                duration = time.time() - start_time
                user_output = process.stdout.strip()

                if process.returncode != 0:
                    verdict = f"{Colors.FAIL}RTE (Runtime Error) 💥{Colors.ENDC}"
                    # نمایش خطای استاندارد برای دیباگ
                    if process.stderr:
                        print(f"   Error: {process.stderr.strip()}")

                elif user_output == expected_output:
                    verdict = f"{Colors.OKGREEN}ACCEPTED ✅{Colors.ENDC}"
                    ac_count += 1
                else:
                    verdict = f"{Colors.FAIL}WRONG ANSWER ❌{Colors.ENDC}"
                    # اگر خواستی بدانی چرا غلط شده، خط زیر را از کامنت دربیار:
                    # print(f"   Expected: {expected_output[:20]}... | Got: {user_output[:20]}...")

        except subprocess.TimeoutExpired:
            verdict = f"{Colors.WARNING}TLE (Time Limit Exceeded) ⏳{Colors.ENDC}"
            duration = DEFAULT_TIME_LIMIT

        # چاپ نتیجه این تست
        print(f"Test {test_in:<10} : {verdict} ({duration:.3f}s)")

        # اگر کاربر INTJ هستی و نمی‌خواهی وقتت تلف شود، با اولین خطا متوقف شو (اختیاری)
        # if "ACCEPTED" not in verdict: break

    print("-" * 50)

    # نتیجه نهایی
    if ac_count == total_count and total_count > 0:
        print(
            f"{Colors.OKGREEN}{Colors.BOLD}🎉 CONGRATULATIONS! ALL TESTS PASSED ({ac_count}/{total_count}){Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}💀 FAILED. Passed {ac_count} out of {total_count} tests.{Colors.ENDC}")

    # پاک کردن فایل اجرایی
    if os.path.exists(exe_file):
        os.remove(exe_file)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"{Colors.HEADER}CSES Offline Judge{Colors.ENDC}")
        print("Usage: python3 judge.py <PROBLEM_ID> <YOUR_CODE.cpp>")
        print("Example: python3 judge.py 1068 solution.cpp")
    else:
        p_id = sys.argv[1]
        c_file = sys.argv[2]
        run_tests(p_id, c_file)
