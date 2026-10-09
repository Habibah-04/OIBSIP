import json, socket, threading, sqlite3, hashlib, secrets
from datetime import datetime
from pathlib import Path

HOST, PORT = "127.0.0.1", 5055
DB = Path(__file__).with_name("chat_history.db")
clients = {}  # socket -> {username, room, send_lock}
lock = threading.Lock()

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY, salt TEXT NOT NULL, password_hash TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL,
            username TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL)""")

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()

def send(sock, payload):
    data=(json.dumps(payload,ensure_ascii=False)+"\n").encode("utf-8")
    try:
        with clients.get(sock,{}).get("send_lock",threading.Lock()):
            sock.sendall(data)
    except Exception:
        pass

def broadcast(room, payload, exclude=None):
    with lock: targets=[s for s,info in clients.items() if info["room"]==room and s!=exclude]
    for sock in targets: send(sock,payload)

def authenticate(action, username, password):
    if not username or len(username)>24 or not username.replace("_","").isalnum(): return False,"Username must be 1–24 letters, numbers or underscores."
    if len(password)<8: return False,"Password must contain at least 8 characters."
    with sqlite3.connect(DB) as con:
        row=con.execute("SELECT salt,password_hash FROM users WHERE username=?",(username,)).fetchone()
        if action=="register":
            if row: return False,"That username already exists."
            salt=secrets.token_hex(16); digest=hash_password(password,salt)
            con.execute("INSERT INTO users VALUES(?,?,?)",(username,salt,digest))
            return True,"Account created."
        if not row or not secrets.compare_digest(row[1],hash_password(password,row[0])):
            return False,"Incorrect username or password."
        return True,"Signed in."

def history(room):
    with sqlite3.connect(DB) as con:
        return con.execute("SELECT username,message,created_at FROM messages WHERE room=? ORDER BY id DESC LIMIT 40",(room,)).fetchall()[::-1]

def handle(sock, address):
    file=sock.makefile("r",encoding="utf-8")
    try:
        first=json.loads(file.readline())
        ok,msg=authenticate(first.get("action"),first.get("username","").strip(),first.get("password",""))
        send(sock,{"type":"auth","ok":ok,"message":msg})
        if not ok: return
        username=first["username"].strip(); room="general"
        with lock: clients[sock]={"username":username,"room":room,"send_lock":threading.Lock()}
        send(sock,{"type":"history","room":room,"messages":[{"username":u,"message":m,"time":t} for u,m,t in history(room)]})
        broadcast(room,{"type":"system","message":f"{username} joined #{room}."},exclude=sock)
        for line in file:
            try: payload=json.loads(line)
            except Exception: continue
            typ=payload.get("type")
            if typ=="room":
                new=payload.get("room","general").strip().lower()
                if not new.replace("_","").isalnum() or len(new)>24:
                    send(sock,{"type":"system","message":"Room names must use letters, numbers or underscores (max 24)."}); continue
                broadcast(room,{"type":"system","message":f"{username} left #{room}."},exclude=sock)
                room=new
                with lock:
                    if sock in clients: clients[sock]["room"]=room
                send(sock,{"type":"history","room":room,"messages":[{"username":u,"message":m,"time":t} for u,m,t in history(room)]})
                broadcast(room,{"type":"system","message":f"{username} joined #{room}."},exclude=sock)
            elif typ=="message":
                message=payload.get("message","").strip()
                if not message: continue
                message=message[:1000]; stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with sqlite3.connect(DB) as con: con.execute("INSERT INTO messages(room,username,message,created_at) VALUES(?,?,?,?)",(room,username,message,stamp))
                broadcast(room,{"type":"message","username":username,"message":message,"time":stamp})
    except Exception as e:
        print(f"Client {address} disconnected: {e}")
    finally:
        with lock:
            info=clients.pop(sock,None)
        if info: broadcast(info["room"],{"type":"system","message":f"{info['username']} disconnected."},exclude=sock)
        try: file.close(); sock.close()
        except Exception: pass

if __name__=="__main__":
    init_db()
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind((HOST,PORT)); server.listen()
    print(f"OIBSIP Chat server listening on {HOST}:{PORT}")
    try:
        while True:
            sock,addr=server.accept()
            threading.Thread(target=handle,args=(sock,addr),daemon=True).start()
    except KeyboardInterrupt: print("Stopping server…")
    finally: server.close()
