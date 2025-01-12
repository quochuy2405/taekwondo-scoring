# Sử dụng parent image python:3.9-slim-buster
FROM python:3.9-slim-buster

# Thiết lập working directory
WORKDIR /app

# Copy file requirements.txt vào trong image
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install -r requirements.txt

# Copy source code vào trong image
COPY . .

# Copy script start.sh và cấp quyền thực thi
COPY start.sh .
RUN chmod +x start.sh

# Khai báo thông tin port 5000 cho ứng dụng
EXPOSE 5000

# Đặt biến môi trường
ENV FLASK_APP=app.py
ENV QR_APP=qr.py

# Command để khởi chạy script
CMD ["./start.sh"]
