import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB = Path(__file__).with_name("bmi_history.db")
BG, CARD, TEXT, MUTED, TEAL = "#0b1220", "#142136", "#e7eef9", "#9aabc4", "#35d0b0"

def connect():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS records(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        weight REAL NOT NULL, height REAL NOT NULL, bmi REAL NOT NULL,
        category TEXT NOT NULL, created_at TEXT NOT NULL)""")
    return con

def classify(bmi):
    if bmi < 18.5: return "Underweight", "#72b7ff"
    if bmi < 25: return "Normal", "#35d0b0"
    if bmi < 30: return "Overweight", "#ffca70"
    return "Obese", "#ff7777"

class BMIApp:
    def __init__(self, root):
        self.root=root; root.title("BMI Studio | OIBSIP"); root.geometry("980x720"); root.minsize(820,620); root.configure(bg=BG)
        self.name=tk.StringVar(); self.weight=tk.StringVar(); self.height=tk.StringVar(); self.result=tk.StringVar(value="Your result will appear here")
        self.setup_style(); self.build(); self.refresh()
    def setup_style(self):
        s=ttk.Style(); s.theme_use("clam")
        s.configure("TLabel",background=BG,foreground=TEXT,font=("Segoe UI",10))
        s.configure("Title.TLabel",font=("Segoe UI",24,"bold"),foreground=TEAL)
        s.configure("TButton",padding=8,font=("Segoe UI",10,"bold"))
        s.configure("Treeview",background=CARD,foreground=TEXT,fieldbackground=CARD,rowheight=27)
        s.configure("Treeview.Heading",background="#20324a",foreground=TEXT)
    def build(self):
        head=ttk.Frame(self.root,padding=(24,20)); head.pack(fill="x")
        ttk.Label(head,text="BMI STUDIO",style="Title.TLabel").pack(anchor="w")
        ttk.Label(head,text="Track measurements over time • private local SQLite history").pack(anchor="w",pady=(4,0))
        body=ttk.Frame(self.root,padding=(24,4)); body.pack(fill="both",expand=True)
        left=tk.Frame(body,bg=CARD,padx=20,pady=20); left.pack(side="left",fill="y",padx=(0,16))
        tk.Label(left,text="NEW MEASUREMENT",bg=CARD,fg=TEAL,font=("Segoe UI",12,"bold")).pack(anchor="w",pady=(0,16))
        for label,var,hint in [("Name",self.name,"e.g. Alex"),("Weight (kg)",self.weight,"e.g. 65.5"),("Height (cm)",self.height,"e.g. 168")]:
            tk.Label(left,text=label,bg=CARD,fg=TEXT,font=("Segoe UI",10)).pack(anchor="w")
            tk.Entry(left,textvariable=var,font=("Segoe UI",11),bg="#0e1727",fg=TEXT,insertbackground=TEXT,relief="flat",width=27).pack(fill="x",ipady=9,pady=(5,13))
        tk.Button(left,text="Calculate & Save",command=self.calculate,bg=TEAL,fg="#06121d",relief="flat",font=("Segoe UI",10,"bold"),padx=12,pady=10).pack(fill="x")
        tk.Label(left,textvariable=self.result,bg=CARD,fg=TEXT,font=("Segoe UI",12,"bold"),wraplength=240,justify="left").pack(anchor="w",pady=20)
        ttk.Button(left,text="Refresh history",command=self.refresh).pack(fill="x")
        ttk.Button(left,text="Show selected user trend",command=self.plot).pack(fill="x",pady=(8,0))
        right=ttk.Frame(body); right.pack(side="left",fill="both",expand=True)
        ttk.Label(right,text="RECENT RECORDS",font=("Segoe UI",13,"bold")).pack(anchor="w",pady=(0,8))
        cols=("date","name","weight","height","bmi","category")
        self.tree=ttk.Treeview(right,columns=cols,show="headings",height=9)
        for c,w in zip(cols,(135,100,75,75,70,100)): self.tree.heading(c,text=c.title()); self.tree.column(c,width=w,anchor="center")
        self.tree.pack(fill="x")
        self.fig=Figure(figsize=(6,3.1),dpi=90); self.ax=self.fig.add_subplot(111); self.fig.patch.set_facecolor(CARD); self.ax.set_facecolor(CARD)
        self.canvas=FigureCanvasTkAgg(self.fig,master=right); self.canvas.get_tk_widget().pack(fill="both",expand=True,pady=(14,0))
        tk.Label(self.root,text="BMI is a screening measure, not a medical diagnosis.",bg=BG,fg=MUTED,font=("Segoe UI",9)).pack(pady=(0,12))
    def calculate(self):
        try:
            name=self.name.get().strip()
            weight=float(self.weight.get()); height=float(self.height.get())/100
            if not name: raise ValueError("Enter a name.")
            if weight<=0 or not 0.5<=height<=2.7: raise ValueError("Weight must be positive and height must be between 50 and 270 cm.")
            bmi=weight/(height*height); category,color=classify(bmi)
            with connect() as con: con.execute("INSERT INTO records(name,weight,height,bmi,category,created_at) VALUES(?,?,?,?,?,?)",(name,weight,height*100,bmi,category,datetime.now().isoformat(timespec="seconds")))
            self.result.set(f"BMI {bmi:.2f}\n{category}\nRecord saved for {name}.")
            self.refresh(name)
        except ValueError as e: messagebox.showerror("Check input",str(e))
        except sqlite3.Error as e: messagebox.showerror("Database error",f"Could not save record:\n{e}")
    def refresh(self, selected_name=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        try:
            with connect() as con: rows=con.execute("SELECT created_at,name,weight,height,bmi,category FROM records ORDER BY id DESC LIMIT 100").fetchall()
            for row in rows: self.tree.insert("", "end", values=(row[0].replace("T"," "),row[1],f"{row[2]:.1f}",f"{row[3]:.1f}",f"{row[4]:.2f}",row[5]))
            self.plot(selected_name, quiet=True)
        except sqlite3.Error as e: messagebox.showerror("Database error",str(e))
    def plot(self, selected_name=None, quiet=False):
        name=(selected_name or self.name.get().strip())
        if not name:
            sel=self.tree.selection()
            if sel: name=self.tree.item(sel[0],"values")[1]
        self.ax.clear(); self.ax.set_facecolor(CARD); self.ax.tick_params(colors=TEXT); self.ax.title.set_color(TEXT); self.ax.xaxis.label.set_color(TEXT); self.ax.yaxis.label.set_color(TEXT)
        if name:
            try:
                with connect() as con: rows=con.execute("SELECT created_at,bmi FROM records WHERE name=? ORDER BY id",(name,)).fetchall()
                if rows:
                    self.ax.plot(range(1,len(rows)+1),[r[1] for r in rows],marker="o",linewidth=2)
                    self.ax.set_title(f"BMI trend — {name}"); self.ax.set_xlabel("Record"); self.ax.set_ylabel("BMI"); self.ax.grid(alpha=.2)
                elif not quiet: messagebox.showinfo("No history",f"No records found for {name}.")
            except sqlite3.Error as e:
                if not quiet: messagebox.showerror("Database error",str(e))
        else: self.ax.set_title("Enter a name and save a measurement to start a trend.")
        self.fig.tight_layout(); self.canvas.draw()
if __name__=="__main__":
    root=tk.Tk(); BMIApp(root); root.mainloop()
