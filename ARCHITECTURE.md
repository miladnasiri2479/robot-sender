# 🏗️ Architecture & System Design: Soroush Multi-Messenger Syncer

This document provides a deep dive into how the synchronization system is built, the logic behind its design, and how it handles message flow between platforms.

---

## 🚀 The Core Philosophy
The system is designed as a **Modular Distributed Task Pipeline**. Instead of a single script trying to talk to 5 different platforms at once (which is prone to failure), we treat every message as a "Task" that needs to be fulfilled by specialized "Workers".

## 🛠️ System Components

### 1. The Ingestion Layer (Soroush Poller)
- **Role:** The "Ear" of the system.
- **How it works:** Every minute (configurable), a scheduled Celery Beat task triggers a poll to the Soroush Plus API.
- **Responsibility:** It fetches new messages, normalizes them into a standard JSON format, and checks the database to see if we've seen this ID before.

### 2. The Persistence Layer (PostgreSQL)
- **Role:** The "Memory".
- **How it works:** We use a `MessageLog` table.
- **Responsibility:** 
    - **Duplicate Prevention:** Before doing anything, the system checks if a Soroush Message ID exists. If yes, it's ignored.
    - **State Tracking:** We track the status of each platform (`pending`, `success`, `failed`, `error`). You can see exactly which platform failed for which message.

### 3. The Queue Layer (Redis)
- **Role:** The "Buffer".
- **How it works:** When a new message is found, the system doesn't send it immediately. It drops a "Task" into Redis.
- **Responsibility:** This decouples the discovery of a message from the actual sending. If Telegram is slow, it won't stop the Eitaa worker from finishing its job.

### 4. The Worker Layer (Celery Workers)
- **Role:** The "Hands".
- **How it works:** Independent processes that pick up tasks from Redis.
- **Responsibility:** They use **Platform Adapters** to talk to APIs.
- **Retry Logic:** If a worker fails (e.g., Internet goes down or Rubika API returns 500), it uses **Exponential Backoff**. It retries after 1 min, then 2 mins, then 4 mins... up to 5 times.

### 5. The Adapter Layer (Platform Adapters)
- **Role:** The "Translators".
- **How it works:** Each platform (Bale, Eitaa, Rubika, Telegram) has its own class.
- **Responsibility:** They translate our internal "Standard Message" into the specific JSON or Multipart format required by that messenger's API.

---

## 🔄 Message Life-Cycle

1.  **Detection:** Soroush Poller finds a new Video post with ID `123`.
2.  **Logging:** ID `123` is saved to Postgres with status `pending`.
3.  **Fan-out:** A main task triggers 4 sub-tasks (one for each platform).
4.  **Execution:**
    - **Telegram Worker:** Downloads video -> Uploads to Telegram -> Updates status to `success`.
    - **Eitaa Worker:** Downloads video -> Uploads to Eitaayar -> Updates status to `success`.
    - ... and so on.
5.  **Completion:** All statuses are updated. You can query `GET /logs` to see the full history.

## 🛡️ Resilience Features
- **Network Timeouts:** All API calls have a 30-60 second timeout to prevent hanging.
- **Independent Failure:** If Eitaa is down, Telegram and Bale will still work perfectly.
- **Scalability:** You can run 10 workers in parallel if you have a very high-traffic channel.
