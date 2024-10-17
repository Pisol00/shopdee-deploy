# ใช้ image ของ Python เป็น base
FROM python:3.11

# ตั้ง working directory
WORKDIR /app

# คัดลอกไฟล์ requirements.txt
COPY requirements.txt .

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอก source code
COPY . .

# รันคำสั่งเพื่อทำ migrations
RUN python manage.py migrate

# รันเซิร์ฟเวอร์ด้วย gunicorn
CMD ["gunicorn", "shopdee.wsgi:application", "--bind", "0.0.0.0:8000"]
