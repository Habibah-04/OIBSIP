import json, socket, threading, tkinter as tk
from tkinter import ttk, messagebox, simpledialog
HOST, PORT = "127.0.0.1", 5055
BG, CARD, TEXT, MUTED, ACCENT = "#0b1220", "#142136", "#e7eef9", "#9aabc4", "#35d0b0"

class ChatClient:
    def __init__(self, root):
        self.root=root; root.title("OIBSIP Chat | Sign in"); root.geometry("760x640"); root.minsize(620,520); root.configure(bg=BG)
        self.sock=None; self.file=None; self.username=""; self.room="general"; self.build_login()
        root.protocol("WM_DELETE_WINDOW",self.close)
    def build_login(self):
        self.clear()
        tk.Label(self.root,text="OIBSIP / CHAT",bg=BG,fg=ACCENT,font=("Segoe UI",24,"bold")).pack(anchor="w",padx=28,pady=(26,4))
        tk.Label(self.root,text="MULTI-ROOM MESSAGING • LOCAL TCP SERVER",bg=BG,fg=MUTED,font=("Segoe UI",10)).pack(anchor="w",padx=29,pady=(0,20))
        card=tk.Frame(self.root,bg=CARD,padx=26,pady=24); card.pack(padx=28,fill="x")
        self.user=tk.StringVar(); self.password=tk.StringVar(); self.action=tk.StringVar(value="register")
        for label,var,show in [("Username",self.user,None),("Password (min. 8 characters)",self.password,"•")]:
            tk.Label(card,text=label,bg=CARD,fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(5,5))
            tk.Entry(card,textvariable=var,show=show,font=("Segoe UI",11),bg="#0e1727",fg=TEXT,insertbackground=TEXT,relief="flat").pack(fill="x",ipady=10,pady=(0,12))
        row=tk.Frame(card,bg=CARD); row.pack(fill="x")
        ttk.Radiobutton(row,text="Create account",variable=self.action,value="register").pack(side="left")
        ttk.Radiobutton(row,text="Sign in",variable=self.action,value="login").pack(side="left",padx=18)
        tk.Button(card,text="Connect to chat",command=self.connect,bg=ACCENT,fg="#06121d",relief="flat",font=("Segoe UI",10,"bold"),pady=10).pack(fill="x",pady=(18,0))
        tk.Label(self.root,text="Start server.py in another terminal before connecting.",bg=BG,fg=MUTED).pack(pady=14)
    def connect(self):
        try:
            self.sock=socket.create_connection((HOST,PORT),timeout=5); self.sock.settimeout(None)
            self.file=self.sock.makefile("r",encoding="utf-8")
            self.send({"action":self.action.get(),"username":self.user.get().strip(),"password":self.password.get()})
            response=json.loads(self.file.readline())
            if not response.get("ok"):
                messagebox.showerror("Sign-in failed",response.get("message","Authentication failed")); self.sock.close(); self.sock=None; return
            self.username=self.user.get().strip()
            self.build_chat()
            threading.Thread(target=self.receive,daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection failed",f"Could not connect to {HOST}:{PORT}.\nStart server.py first.\n\n{e}")
            try:
                if self.sock: self.sock.close()
            except Exception: pass
            self.sock=None
    def build_chat(self):
        self.clear(); self.root.title(f"OIBSIP Chat | {self.username}")
        top=tk.Frame(self.root,bg=BG,padx=22,pady=16); top.pack(fill="x")
        tk.Label(top,text="CHAT ROOM",bg=BG,fg=ACCENT,font=("Segoe UI",19,"bold")).pack(side="left")
        tk.Label(top,text=f"Signed in as {self.username}",bg=BG,fg=MUTED).pack(side="left",padx=18)
        tk.Button(top,text="Change room",command=self.change_room,bg="#263a52",fg=TEXT,relief="flat").pack(side="right")
        self.room_label=tk.Label(self.root,text="#general",bg=BG,fg=TEXT,font=("Segoe UI",11,"bold")); self.room_label.pack(anchor="w",padx=24)
        self.chat=tk.Text(self.root,bg=CARD,fg=TEXT,relief="flat",font=("Segoe UI",10),wrap="word",padx=14,pady=12,state="disabled")
        self.chat.pack(fill="both",expand=True,padx=22,pady=12)
        bottom=tk.Frame(self.root,bg=BG,padx=22,pady=10); bottom.pack(fill="x")
        self.msg=tk.StringVar(); entry=tk.Entry(bottom,textvariable=self.msg,bg="#0e1727",fg=TEXT,insertbackground=TEXT,relief="flat",font=("Segoe UI",11))
        entry.pack(side="left",fill="x",expand=True,ipady=10); entry.bind("<Return>",lambda e:self.send_message())
        tk.Button(bottom,text="Send",command=self.send_message,bg=ACCENT,fg="#06121d",relief="flat",font=("Segoe UI",10,"bold"),padx=20).pack(side="left",padx=(10,0))
    def clear(self):
        for w in self.root.winfo_children(): w.destroy()
    def send(self,payload):
        if self.sock:
            try: self.sock.sendall((json.dumps(payload,ensure_ascii=False)+"\n").encode("utf-8"))
            except Exception as e: self.root.after(0,lambda:messagebox.showerror("Network error",str(e)))
    def send_message(self):
        text=self.msg.get().strip()
        if text: self.send({"type":"message","message":text}); self.msg.set("")
    def change_room(self):
        room=simpledialog.askstring("Change room","Room name (letters, numbers, underscores):",initialvalue=self.room,parent=self.root)
        if room and room.strip(): self.send({"type":"room","room":room.strip()})
    def receive(self):
        try:
            for line in self.file:
                data=json.loads(line); self.root.after(0,self.render,data)
        except Exception as e:
            self.root.after(0,self.append,"System",f"Connection closed: {e}","")
    def render(self,data):
        if data.get("type")=="history":
            self.room=data.get("room","general"); self.room_label.config(text="#"+self.room)
            self.chat.config(state="normal"); self.chat.delete("1.0","end")
            for m in data.get("messages",[]): self.append(m["username"],m["message"],m["time"],redraw=False)
            self.chat.config(state="disabled"); self.chat.see("end")
        elif data.get("type")=="message": self.append(data.get("username","?"),data.get("message",""),data.get("time",""))
        elif data.get("type")=="system": self.append("•",data.get("message",""),"")
    def append(self,user,text,stamp="",redraw=True):
        if not hasattr(self,"chat"): return
        self.chat.config(state="normal")
        prefix=f"[{stamp}] " if stamp else ""
        self.chat.insert("end",f"{prefix}{user}: {text}\n")
        self.chat.config(state="disabled"); self.chat.see("end")
    def close(self):
        try:
            if self.sock: self.sock.shutdown(socket.SHUT_RDWR); self.sock.close()
        except Exception: pass
        self.root.destroy()
if __name__=="__main__":
    root=tk.Tk(); ChatClient(root); root.mainloop()
