# 🤖 Robot Sender (Multi-Messenger Syncer)

[**English**](./README.md) | [**فارسی**](./README.fa.md)

---

## 🏗️ System Architecture & Workflow

### 1. Visual Flowchart
```mermaid
graph TD
    subgraph "Phase 1: Discovery"
        S[Soroush Channel] -->|Polls every 60s| Ingest[Ingestion Service]
    end

    subgraph "Phase 2: Processing"
        Ingest -->|Normalize| Norm[Standard Message Format]
        Norm -->|Unique ID Check| DB[(PostgreSQL)]
        DB -->|If New| Queue[Redis Task Queue]
    end

    subgraph "Phase 3: Dispatch & Delivery"
        Queue -->|Task 1| TW[Telegram Worker]
        Queue -->|Task 2| EW[Eitaa Worker]
        Queue -->|Task 3| RW[Rubika Worker]
        Queue -->|Task 4| BW[Bale Worker]
        
        TW -->|API Call| TG((Telegram))
        EW -->|API Call| ET((Eitaa))
        RW -->|API Call| RB((Rubika))
        BW -->|API Call| BL((Bale))
    end

    subgraph "Phase 4: Feedback"
        TG & ET & RB & BL -->|Log Result| DB
    end
```

---

### 2. How it works (Step-by-Step)

1.  **Polling (Detection):** Every minute, the "Ingestion Service" asks the Soroush Plus API: "Are there any new posts?".
2.  **Normalization:** When a new post arrives (e.g., an Image with a caption), the system converts it into a **Universal Format**. It doesn't matter if it came from Soroush; it's now just a "Standard Image Task".
3.  **Deduplication:** The system checks the **PostgreSQL** database. If the Message ID `XYZ` was already synced before, it stops here to prevent spamming your channels.
4.  **Task Queuing:** If it's a new message, the system creates 4 separate instructions (Tasks) and puts them into **Redis**. 
5.  **Parallel Execution:** 4 independent "Workers" (one for each messenger) wake up. They work **at the same time**. 
    - If Telegram is slow, Eitaa doesn't wait. It finishes its job immediately.
    - If Rubika's API is down, its worker will keep retrying every few minutes without affecting Bale or Telegram.
6.  **Reporting:** Once a message is successfully sent (or permanently fails), the result is written back to the database so you can monitor it via the `/logs` endpoint.

---

## ✨ Features
- **🔄 Multi-Platform Sync:** Supports Text, Photos, Videos, and Files.
- **🛡️ Distributed Workers:** Each platform is handled by an independent process.
- **🔄 Exponential Backoff:** Automatic retries for failed tasks (1m, 2m, 4m...).
- **🚫 Anti-Duplicate:** PostgreSQL ensures no double-posting.
- **🐳 One-Click Deploy:** Fully containerized with Docker Compose.

---

## 🚀 Quick Setup

1. **Clone & Configure:**
   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

2. **Deploy:**
   ```bash
   docker-compose up -d --build
   ```

3. **Monitor:**
   - Health: `http://localhost:8000/health`
   - Logs: `docker-compose logs -f worker`

---

## 📝 Iranian Messenger Tips
- **Eitaa:** Get token from [Eitaayar](https://eitaayar.ir) and add `@sender` as admin.
- **Soroush:** Use `@mrbot` in Soroush Plus for tokens.
- **Bale/Rubika:** Use `@BotFather` within the apps.

---

## 📜 License
MIT License.
