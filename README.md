# 🤖 Soroush Multi-Messenger Syncer

[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688.svg)](https://fastapi.tiangolo.com/)

An enterprise-grade synchronization bot that mirrors content from a **Soroush Plus** channel to **Telegram, Eitaa, Rubika, and Bale** in real-time.

---

## ✨ Features

- **🔄 Full Media Support:** Synchronizes Text, Photos, Videos, and Files.
- **🛡️ Rock-Solid Reliability:** Built with Celery & Redis for asynchronous task handling.
- **🔄 Smart Retries:** Automatic exponential backoff if a platform's API is temporarily down.
- **🚫 Zero Duplicates:** PostgreSQL-backed message logging ensures content is never posted twice.
- **📊 Monitoring API:** REST endpoints to check health and view synchronization logs.
- **🐳 Dockerized:** One-command deployment for all services.

---

## 🏗️ How it Works

The system polls your Soroush channel for new content. Once a new post is detected, it normalizes the data and fans out individual tasks for each target platform. This ensures that a failure on one platform (e.g., a Telegram timeout) doesn't affect the others.

> **Read more:** [System Architecture Details](./ARCHITECTURE.md)

---

## 🚀 Deployment Guide

### 1. Prerequisites
- A Linux server (VPS) or local machine with **Docker** and **Docker Compose** installed.
- Bot tokens for all 5 platforms (Soroush, Telegram, Eitaa, Rubika, Bale).

### 2. Prepare Configuration
Clone this repository and create your environment file:
```bash
cp .env.example .env
```
Edit the `.env` file and fill in your credentials:
```env
# Bot Tokens
SOROUSH_TOKEN=...
TELEGRAM_TOKEN=...
EITAA_TOKEN=...
RUBIKA_TOKEN=...
BALE_TOKEN=...

# Channel IDs
SOROUSH_CHANNEL_ID=...
TELEGRAM_CHANNEL_ID=@my_channel
...
```

### 3. Launch the Stack
Run the following command to start the Database, Redis, Web API, and Workers:
```bash
docker-compose up -d --build
```

### 4. Verify the Status
Once started, you can check if everything is running correctly:
- **API Status:** `http://your-server-ip:8000/health`
- **Sync Logs:** `http://your-server-ip:8000/logs`
- **Real-time Logs:** `docker-compose logs -f worker`

---

## 🛠️ API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | System version and basic status. |
| `/health` | `GET` | Database and connectivity check. |
| `/logs` | `GET` | View recent synchronization history. |
| `/sync/trigger` | `POST` | Manually force a poll for new messages. |

---

## 📝 Iranian Messenger Bot Setup Tips
- **Eitaa:** You must get your token from [Eitaayar](https://eitaayar.ir) and add the `@sender` bot as an administrator to your channel.
- **Soroush:** Use the `@mrbot` in Soroush Plus to create your bot and get the token.
- **Rubika/Bale:** Use their respective `@BotFather` accounts within the apps.

---

## 🤝 Contributing
Contributions are welcome! If you want to add a new platform (like Gap or Virasty), simply create a new adapter in `src/adapters/` and add it to the tasks.

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
