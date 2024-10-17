# ใช้ image ของ Python
FROM python:3.11-slim

# กำหนด working directory
WORKDIR /app

# คัดลอก requirements.txt เข้ามาใน container
COPY requirements.txt .

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอก source code ทั้งหมดเข้าไปใน container
COPY . .

# รัน migrations
RUN python manage.py migrate

# รัน server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "shopdee.wsgi:application"]
