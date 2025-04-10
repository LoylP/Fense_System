FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install

COPY . .

# Build Next.js app
RUN npm run build

# 🔥 Set PORT to 8000
ENV PORT=8000

# Expose port 8000
EXPOSE 8000

# Start app
CMD ["npm", "start"]