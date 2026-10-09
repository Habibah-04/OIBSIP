import secrets, string, tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

BG, CARD, TEXT, MUTED, ACCENT = "#0b1220", "#142136", "#e7eef9", "#9aabc4", "#35d0b0"
AMBIGUOUS = set("0Ool1I")

class PasswordApp:
    def __init__(self, root):
        self.root=root; root.title("CipherLab | Password Generator"); root.geometry("760x660"); root.minsize(650,580); root.configure(bg=BG)
        self.length=tk.IntVar(value=20); self.upper=tk.BooleanVar(value=True); self.lower=tk.BooleanVar(value=True); self.digits=tk.BooleanVar(value=True); self.symbols=tk.BooleanVar(value=True); self.exclude=tk.BooleanVar(value=True)
        self.password=tk.StringVar(); self.strength=tk.StringVar(value="Generate a password to analyse strength"); self.history=[]
        self.build()
    def build(self):
        tk.Label(self.root,text="CIPHERLAB",bg=BG,fg=ACCENT,font=("Segoe UI",24,"bold")).pack(anchor="w",padx=28,pady=(24,0))
        tk.Label(self.root,text="Secure password generation • powered by secrets",bg=BG,fg=MUTED,font=("Segoe UI",10)).pack(anchor="w",padx=29,pady=(2,18))
        card=tk.Frame(self.root,bg=CARD,padx=22,pady=20); card.pack(fill="x",padx=26)
        row=tk.Frame(card,bg=CARD); row.pack(fill="x")
        tk.Label(row,text="PASSWORD LENGTH",bg=CARD,fg=TEXT,font=("Segoe UI",10,"bold")).pack(side="left")
        tk.Spinbox(row,from_=8,to=128,textvariable=self.length,width=7,font=("Segoe UI",11),bg="#0e1727",fg=TEXT,buttonbackground="#20324a").pack(side="right")
        tk.Scale(card,from_=8,to=128,orient="horizontal",variable=self.length,bg=CARD,fg=TEXT,highlightthickness=0,troughcolor="#263a52",length=550).pack(fill="x",pady=(5,12))
        tk.Label(card,text="CHARACTER SETS (select at least two)",bg=CARD,fg=ACCENT,font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(0,8))
        opts=tk.Frame(card,bg=CARD); opts.pack(fill="x")
        for label,var in [("Uppercase A–Z",self.upper),("Lowercase a–z",self.lower),("Numbers 0–9",self.digits),("Symbols !@#",self.symbols)]:
            tk.Checkbutton(opts,text=label,variable=var,bg=CARD,fg=TEXT,selectcolor="#0e1727",activebackground=CARD,activeforeground=TEXT).pack(side="left",padx=(0,12))
        tk.Checkbutton(card,text="Exclude ambiguous characters (0, O, l, 1, I)",variable=self.exclude,bg=CARD,fg=TEXT,selectcolor="#0e1727",activebackground=CARD,activeforeground=TEXT).pack(anchor="w",pady=(12,0))
        tk.Button(card,text="Generate secure password",command=self.generate,bg=ACCENT,fg="#06121d",relief="flat",font=("Segoe UI",10,"bold"),pady=10).pack(fill="x",pady=(16,0))
        out=tk.Frame(self.root,bg=CARD,padx=22,pady=18); out.pack(fill="x",padx=26,pady=16)
        tk.Label(out,text="GENERATED PASSWORD",bg=CARD,fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w")
        self.out=tk.Entry(out,textvariable=self.password,font=("Consolas",15),bg="#0e1727",fg=TEXT,insertbackground=TEXT,relief="flat")
        self.out.pack(fill="x",ipady=12,pady=8)
        actions=tk.Frame(out,bg=CARD); actions.pack(fill="x")
        tk.Button(actions,text="Copy to clipboard",command=self.copy,bg="#263a52",fg=TEXT,relief="flat",pady=8).pack(side="left")
        tk.Label(actions,textvariable=self.strength,bg=CARD,fg=ACCENT,font=("Segoe UI",10,"bold")).pack(side="left",padx=14)
        hist=tk.Frame(self.root,bg=BG,padx=28); hist.pack(fill="both",expand=True)
        tk.Label(hist,text="SESSION HISTORY  ·  last 5 only",bg=BG,fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w")
        self.hist=tk.Listbox(hist,bg="#0e1727",fg=TEXT,relief="flat",font=("Consolas",10),height=5,selectbackground="#244c57")
        self.hist.pack(fill="both",expand=True,pady=8)
        tk.Label(self.root,text="Passwords are not saved to disk. Store generated credentials in a trusted password manager.",bg=BG,fg=MUTED,font=("Segoe UI",9)).pack(pady=(0,16))
    def generate(self):
        try: n=int(self.length.get())
        except Exception: messagebox.showerror("Invalid length","Enter a whole number between 8 and 128."); return
        if not 8<=n<=128: messagebox.showerror("Invalid length","Length must be between 8 and 128."); return
        sets=[]
        if self.upper.get(): sets.append(string.ascii_uppercase)
        if self.lower.get(): sets.append(string.ascii_lowercase)
        if self.digits.get(): sets.append(string.digits)
        if self.symbols.get(): sets.append("!@#$%^&*()-_=+[]{}:,.?")
        if len(sets)<2: messagebox.showerror("Choose character types","Select at least two character types."); return
        if self.exclude.get(): sets=[ ''.join(c for c in s if c not in AMBIGUOUS) for s in sets ]
        chars=''.join(sets)
        # Guarantee at least one from each selected class, then cryptographically shuffle.
        pwd=[secrets.choice(s) for s in sets]
        pwd.extend(secrets.choice(chars) for _ in range(n-len(pwd)))
        for i in range(len(pwd)-1,0,-1):
            j=secrets.randbelow(i+1); pwd[i],pwd[j]=pwd[j],pwd[i]
        value=''.join(pwd); self.password.set(value)
        diversity=len(sets); score=(n>=16)+(n>=24)+(diversity>=3)+(diversity==4)
        level="Strong" if score>=3 else "Medium" if score>=2 else "Weak"
        self.strength.set(f"Strength: {level}")
        self.history.insert(0,value); self.history=self.history[:5]
        self.hist.delete(0,"end")
        for item in self.history: self.hist.insert("end",item)
        try: pyperclip.copy(value)
        except Exception: pass
    def copy(self):
        if not self.password.get(): return
        try: pyperclip.copy(self.password.get()); messagebox.showinfo("Copied","Password copied to clipboard.")
        except Exception: messagebox.showwarning("Clipboard unavailable","Select the password field and copy manually.")
if __name__=="__main__":
    root=tk.Tk(); PasswordApp(root); root.mainloop()
