# 1. استفاده از پایتون نسخه 3.9 (نسخه Slim برای حجم کمتر)
FROM python:3.9-slim

# 2. تنظیم دایرکتوری کاری داخل کانتینر
WORKDIR /app

# 3. نصب پکیج‌های سیستمی ضروری (g++ برای کامپایل کدهای C++)
# دستورات را در یک خط می‌نویسیم تا لایه‌های داکر کمتر شود
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. نصب کتابخانه‌های پایتون مورد نیاز
# (اگر فایل requirements.txt داشتی بهتر بود، ولی اینجا دستی می‌نویسیم)
RUN pip install --no-cache-dir flask beautifulsoup4 requests

# 5. کپی کردن تمام فایل‌های پروژه به داخل کانتینر
COPY . .

# 6. باز کردن پورت 5000 (پورت پیش‌فرض Flask)
EXPOSE 5000

# 7. دستور اجرا هنگام بالا آمدن کانتینر
CMD ["python", "server.py"]