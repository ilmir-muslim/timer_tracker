FROM node:16

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install --timeout=600000

# Копируем исходный код
COPY . .

# Меняем владельца файлов на пользователя node
RUN chown -R node:node /app

# Переключаемся на пользователя node
USER node

EXPOSE 8080
CMD ["npm", "run", "serve", "--", "--port", "8080", "--host", "0.0.0.0"]