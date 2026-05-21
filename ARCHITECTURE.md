# 🏗️ Architecture & System Design: Universal Robot Sender

This document explains the "Universal" design of the Robot Sender, which allows any supported platform to act as a message source or target.

---

## 🚀 The Universal Philosophy
Unlike previous versions that were hardcoded for specific flows, this system uses a **Plugin-based Adapter Architecture**. Every messenger is treated as a "Node" that can either **Read** (fetch messages) or **Write** (send messages).

## 🛠️ System Components

### 1. The Unified Message Model (`src/models.py`)
To make platforms compatible, all incoming messages (regardless of origin) are converted into a `UnifiedMessage`. This object contains:
- `source_id`: The original ID from the source.
- `type`: Text, Image, Video, or File.
- `text`: The caption or body.
- `file_url`: A direct link or ID for the media.

### 2. The Orchestrator (`src/orchestrator.py`)
The Orchestrator is the brain of the system. It:
1.  Asks the **Source Adapter** for new messages.
2.  Filters out messages already in the **SQLite Database**.
3.  Sends new messages to **all Target Adapters** simultaneously using `asyncio.gather`.
4.  Retries failed sends using a safe wrapper.

### 3. The Adapter Layer (`src/adapters/`)
Each file (e.g., `telegram.py`, `soroush.py`) contains a class inheriting from `BaseAdapter`.
- `fetch_messages()`: Implements polling/updates logic.
- `send_message()`: Implements the sending logic.

### 4. The Database (`src/database.py`)
Uses **SQLite** for zero-configuration persistence. It tracks which messages have been successfully synced to prevent duplicates across restarts.

---

## 🔄 How to add a new Platform?

1.  Create a new file in `src/adapters/your_platform.py`.
2.  Inherit from `BaseAdapter`.
3.  Implement `fetch_messages` and `send_message`.
4.  Add your adapter to the `ADAPTERS` dictionary in `main.py`.
5.  Add the credentials to your `config.json`.

---

## 🛡️ Resilience & Performance
- **Async I/O:** Uses `httpx` and `asyncio` for non-blocking network calls.
- **Concurrent Dispatch:** If you have 5 targets, the message is sent to all 5 at the same time, not one by one.
- **Error Isolation:** If one target platform's API is down, it won't block the others.
