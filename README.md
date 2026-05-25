# Party Hard Bar 🍸

Система заказов для бара: Telegram-бот принимает заказы, бармен видит их в веб-интерфейсе в реальном времени.

## Архитектура

```
[Telegram] ──→ [bot] ──→ [backend :40404]
                               ↑
[Browser] → NodePort 30080 → [nginx frontend]
                   ├── /api/*       → backend
                   └── /socket.io/ → backend (WebSocket)
```

Компоненты:
- **backend** — Flask + SocketIO + SQLite
- **frontend** — React + MUI, nginx
- **bot** — python-telegram-bot

## Требования

- Docker
- kubectl + доступ к кластеру (или minikube)

## Быстрый старт

### 1. Настрой `.env`

```bash
cp .env.example .env
```

Содержимое `.env`:
```
TELEGRAM_TOKEN=вставь_сюда_токен_из_@BotFather
API_URL=http://localhost:40404   # если запускаешь локально
```

### 2. Задеплой это счастье

```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Открой интерфейс бармена

- **minikube**: `minikube service bar-frontend -n party-hard`
- **Другой кластер**: `http://<NODE_IP>:30080`

### 4. Найди того, кто будет за бармена и официанта

## Структура проекта

```
pivo_bot/
├── .env
├── .gitignore
├── deploy.sh
├── backend/
│   ├── main.py           # Flask API + SocketIO
│   ├── database.py       # SQLite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   └── components/OrderList.js
│   ├── nginx.conf
│   ├── package.json
│   └── Dockerfile
├── bot/
│   ├── bot.py            # читает TELEGRAM_TOKEN и API_URL из env
│   └── Dockerfile
└── k8s/
    ├── namespace.yaml
    ├── backend-pvc.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml      # ClusterIP :40404
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml     # NodePort 30080
    └── bot-deployment.yaml       # TELEGRAM_TOKEN из Secret, API_URL напрямую
```

## Переменные окружения

| Переменная | Где задаётся | Описание |
|---|---|---|
| `TELEGRAM_TOKEN` | `.env` → K8s Secret | Токен бота от @BotFather |
| `API_URL` | `k8s/bot-deployment.yaml` | URL бэкенда (в K8s задан автоматически) |

## Локальный запуск

```bash
# Бэкенд
cd backend
pip install -r requirements.txt
python main.py

# Фронтенд
cd frontend
npm install --legacy-peer-deps
npm start

# Бот
cd bot
TELEGRAM_TOKEN=вставь_сюда_токен_из_@BotFather API_URL=http://localhost:40404 python bot.py
```

## Чтобы перезапустить, если что-то поменялось:

```bash
./deploy.sh
```

Или только один компонент:
```bash
docker build -t bar-backend:latest ./backend
kubectl rollout restart deployment/bar-backend -n party-hard
```
