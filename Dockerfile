# 🔧 Dùng base image nhẹ và ổn định
FROM python:3.11-slim

# 🏗️ Set thư mục làm việc trong container
WORKDIR /app

# 🧪 Copy file requirements trước để tối ưu layer
COPY requirements.txt ./

# 🧪 Cài đặt các dependency
RUN pip install --no-cache-dir -r requirements.txt

# 🧠 Copy toàn bộ mã nguồn vào container
COPY . .

# 📁 Tạo thư mục chứa database (mount volume sẽ gắn vào đây)
RUN mkdir -p /app/data

# 🌍 Expose port backend
EXPOSE 8080

# ✅ Biến môi trường mặc định (có thể override bằng --env-file khi run)
ENV DB_PATH=/app/data/news_database.db
ENV VECTORDB_PATH=/app/data/ttp_patterns.faiss

# 🚀 Chạy FastAPI bằng uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]