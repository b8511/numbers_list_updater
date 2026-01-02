# numbers_list_updater

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Frontend (index.html)                   │   │
│  │  • Displays number list in table                     │   │
│  │  • Receives real-time updates via SSE                │   │
│  └──────────────────────────────────────────────────────┘   │
│                   │                    ▲                    │
│                   │ HTTP GET           │ SSE Stream         │
│                   │ (/)                │ (/stream)          │
│                   ▼                    │                    │
└─────────────────────────────────────────────────────────────┘
                    │                    │
                    ▼                    │
┌─────────────────────────────────────────────────────────────┐
│              Flask Server (port 5000)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Routes:                                             │   │
│  │  • GET /          → Serve HTML template              │   │
│  │  • GET /get_number_list → Return JSON                │   │
│  │  • GET /stream    → Server-Sent Events               │   │
│  └──────────────────────────────────────────────────────┘   │
│                   ▲                    │                    │
│                   │                    │ broadcast_sse()    │
│                   │ query/update       │                    │
│                   │                    ▼                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           SQLite Database (number_list.db)           │   │
│  │  Table: numbers (value INTEGER PRIMARY KEY)          │   │
│  └──────────────────────────────────────────────────────┘   │
│                   ▲                                         │
│                   │ add_number_to_db()                      │
│                   │ remove_number_from_db()                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │       WebSocket Client Thread                        │   │
│  │  • Connects to ws://localhost:8765                   │   │
│  │  • Receives add/delete messages                      │   │
│  │  • Updates database                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                   ▲                                         │
└───────────────────│─────────────────────────────────────────┘
                    │ WebSocket connection
                    │
┌───────────────────▼─────────────────────────────────────────┐
│       WebSocket Server - local_ws.py (port 8765)            │
│  • Generates random add/delete messages                     │
│  • Sends messages to connected clients                      │
└─────────────────────────────────────────────────────────────┘
```

## Flow

1. **WebSocket Server** generates random add/delete messages
2. **Flask WebSocket Client** receives messages and updates the database
3. **Flask Server** broadcasts SSE notifications to frontend
4. **Frontend** receives SSE notifications and updates table accordingly
