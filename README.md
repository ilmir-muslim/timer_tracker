# ⏱️ Timer Tracker

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-16-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

Приложение для учёта времени выполнения проектов и задач.  
Проект сделан для личного использования, но может быть полезен и коллегам — как бэкендерам, так и фронтендерам.  

---

## 📌 Возможности
- Создание проектов и задач
- Запуск/пауза таймера для каждой задачи
- Подсчёт общего времени по проекту
- Экспорт отчётов в TXT или копирование в буфер
- Современный интерфейс на Vue 3 + Vuex
- REST API на FastAPI (Python 3.11, SQLAlchemy)
- База данных MySQL
- Полностью в Docker (frontend + backend + db)

---

## 🛠️ Стек технологий
- **Backend:** FastAPI, SQLAlchemy, Alembic
- **Frontend:** Vue 3, Vue Router, Vuex, Toastification
- **Database:** MySQL 8.0
- **DevOps:** Docker, Docker Compose

---

## 🚀 Запуск проекта

### 1. Клонирование репозитория
```bash
git clone https://github.com/ilmir-muslim/timer_tracker
cd timer_tracker
```

### 2. Запуск через Docker Compose
```bash
docker compose up --build
```

После запуска:
- Backend: [http://localhost:8000](http://localhost:8000)
- Frontend: [http://localhost:8080](http://localhost:8080)
- Swagger (API документация): [http://localhost:8000/docs](http://localhost:8000/docs)

---


## 📸 Скриншоты

![Скриншот 1](screenshots/Снимок_экрана_20250829_040859.png)
![Скриншот 2](screenshots/Снимок_экрана_20250829_041026.png)




### Пересборка
```bash
docker compose up --build -d
```

### Удаление контейнеров и сети
```bash
docker compose down
```

