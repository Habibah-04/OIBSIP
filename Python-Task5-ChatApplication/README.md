# Task 5 — Chat Application (Advanced)

A multi-room Tkinter chat application with a threaded TCP server, user registration/login, salted PBKDF2 password hashes, timestamps, SQLite message history, room selection, and graceful disconnect notifications.

## Run locally (two or more clients)
Terminal 1:
```powershell
py server.py
```
Terminal 2 and 3:
```powershell
py client.py
```
Clients connect to `127.0.0.1:5055` by default. For another machine on a trusted LAN, update `HOST` in `client.py` to the server's LAN IP and ensure firewall rules allow the port. Do not expose this educational server directly to the public internet; it does not implement TLS, rate limiting, or production-grade session security.
