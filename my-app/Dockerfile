FROM node:20-alpine

# Làm việc tại /app
WORKDIR /app

# 👉 Copy package.json và lock từ thư mục gốc (vì bạn đang ở my-app/)
COPY package.json ./
COPY package-lock.json ./

# Cài dependencies
RUN npm install

# Copy toàn bộ mã nguồn vào container
COPY . .

# Build Next.js
RUN npm run build

# Thiết lập cổng và ENV
ENV PORT=8000
EXPOSE 8000

# Chạy app
CMD ["npm", "start", "--", "-p", "8000"]
