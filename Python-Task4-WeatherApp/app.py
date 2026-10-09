import os, threading, tkinter as tk
from tkinter import ttk
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image, ImageTk

BG, CARD, TEXT, MUTED, ACCENT = "#0b1220", "#142136", "#e7eef9", "#9aabc4", "#35d0b0"
API="https://api.openweathermap.org/data/2.5"

class WeatherApp:
    def __init__(self, root):
        self.root=root; root.title("Atmos | Weather Dashboard"); root.geometry("940x740"); root.minsize(760,640); root.configure(bg=BG)
        self.unit=tk.StringVar(value="Celsius"); self.city=tk.StringVar(value="Lucknow"); self.status=tk.StringVar(value="Enter a city and fetch current conditions.")
        self.icon_img=None; self.build()
    def build(self):
        tk.Label(self.root,text="ATMOS",bg=BG,fg=ACCENT,font=("Segoe UI",25,"bold")).pack(anchor="w",padx=28,pady=(20,0))
        tk.Label(self.root,text="WEATHER DASHBOARD  /  CURRENT + FORECAST",bg=BG,fg=MUTED,font=("Segoe UI",10)).pack(anchor="w",padx=29,pady=(2,15))
        search=tk.Frame(self.root,bg=CARD,padx=16,pady=14); search.pack(fill="x",padx=26)
        tk.Entry(search,textvariable=self.city,font=("Segoe UI",12),bg="#0e1727",fg=TEXT,insertbackground=TEXT,relief="flat").pack(side="left",fill="x",expand=True,ipady=10)
        tk.Button(search,text="Get Weather",command=self.fetch,bg=ACCENT,fg="#06121d",relief="flat",font=("Segoe UI",10,"bold"),padx=18).pack(side="left",padx=10)
        ttk.Combobox(search,textvariable=self.unit,values=("Celsius","Fahrenheit"),state="readonly",width=12).pack(side="left")
        self.unit.trace_add("write",lambda *_: self.redraw())
        self.current=tk.Frame(self.root,bg=CARD,padx=22,pady=18); self.current.pack(fill="x",padx=26,pady=14)
        self.big=tk.Label(self.current,text="—",bg=CARD,fg=TEXT,font=("Segoe UI",34,"bold")); self.big.pack(side="left",padx=(0,22))
        self.icon_label=tk.Label(self.current,bg=CARD); self.icon_label.pack(side="left",padx=8)
        self.details=tk.Label(self.current,text="Current weather will appear here.",bg=CARD,fg=TEXT,font=("Segoe UI",12),justify="left"); self.details.pack(side="left",padx=18)
        self.tabs=ttk.Notebook(self.root); self.tabs.pack(fill="both",expand=True,padx=26,pady=(0,8))
        self.hour_frame=tk.Frame(self.tabs,bg=BG); self.day_frame=tk.Frame(self.tabs,bg=BG)
        self.tabs.add(self.hour_frame,text="Next 6 hours"); self.tabs.add(self.day_frame,text="5-day outlook")
        self.hour_text=tk.Text(self.hour_frame,bg=BG,fg=TEXT,relief="flat",font=("Consolas",11),wrap="word",padx=16,pady=16)
        self.hour_text.pack(fill="both",expand=True)
        self.day_text=tk.Text(self.day_frame,bg=BG,fg=TEXT,relief="flat",font=("Consolas",11),wrap="word",padx=16,pady=16)
        self.day_text.pack(fill="both",expand=True)
        tk.Label(self.root,textvariable=self.status,bg=BG,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=28,pady=(0,14))
        self.data=None
    def fetch(self):
        city=self.city.get().strip()
        if not city: self.status.set("Please enter a city name."); return
        key=os.getenv("OPENWEATHER_API_KEY")
        if not key: self.status.set("Missing OPENWEATHER_API_KEY. Set it in the terminal, then restart this app."); return
        self.status.set("Fetching weather data…")
        threading.Thread(target=self._fetch,args=(city,key),daemon=True).start()
    def _fetch(self,city,key):
        try:
            current=requests.get(API+"/weather",params={"q":city,"appid":key,"units":"metric"},timeout=10)
            forecast=requests.get(API+"/forecast",params={"q":city,"appid":key,"units":"metric"},timeout=10)
            for r in (current,forecast):
                if r.status_code!=200:
                    try: detail=r.json().get("message","Request failed")
                    except Exception: detail=f"HTTP {r.status_code}"
                    raise ValueError(detail)
            data={"current":current.json(),"forecast":forecast.json()}
            self.root.after(0,self.show,data)
        except Exception as e: self.root.after(0,lambda:self.status.set(f"Could not load weather: {e}"))
    def show(self,data):
        self.data=data; self.redraw()
        self.status.set(f"Updated {datetime.now().strftime('%H:%M:%S')} • Forecasts are API estimates.")
    def temp(self,c):
        return c if self.unit.get()=="Celsius" else c*9/5+32
    def redraw(self):
        if not self.data: return
        c=self.data["current"]; f=self.data["forecast"]
        m=c["main"]; w=c["weather"][0]
        unit="°C" if self.unit.get()=="Celsius" else "°F"
        self.big.config(text=f"{self.temp(m['temp']):.1f}{unit}")
        self.details.config(text=f"{c['name']}, {c['sys'].get('country','')}\n{w['description'].title()}\nHumidity  {m['humidity']}%     Wind  {c['wind']['speed']} m/s\nFeels like {self.temp(m['feels_like']):.1f}{unit}     High/Low {self.temp(m['temp_max']):.1f}/{self.temp(m['temp_min']):.1f}{unit}")
        try:
            icon=w["icon"]
            img=Image.open(BytesIO(requests.get(f"https://openweathermap.org/img/wn/{icon}@2x.png",timeout=5).content)).resize((80,80))
            self.icon_img=ImageTk.PhotoImage(img); self.icon_label.config(image=self.icon_img)
        except Exception: self.icon_label.config(image="",text="☁",fg=TEXT,font=("Segoe UI",28))
        self.hour_text.delete("1.0","end")
        for item in f["list"][:6]:
            t=datetime.fromtimestamp(item["dt"]).strftime("%a %H:%M")
            desc=item["weather"][0]["description"].title()
            self.hour_text.insert("end",f"{t:<16} {self.temp(item['main']['temp']):>5.1f}{unit}   {desc:<22} Humidity {item['main']['humidity']}%\n\n")
        groups={}
        for item in f["list"]:
            day=datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            groups.setdefault(day,[]).append(item)
        self.day_text.delete("1.0","end")
        for day,items in list(groups.items())[:5]:
            temps=[self.temp(i["main"]["temp"]) for i in items]
            midday=min(items,key=lambda i:abs(datetime.fromtimestamp(i["dt"]).hour-12))
            desc=midday["weather"][0]["description"].title()
            self.day_text.insert("end",f"{datetime.strptime(day,'%Y-%m-%d').strftime('%A, %d %b')}\n  {min(temps):.1f}{unit} — {max(temps):.1f}{unit}   •   {desc}\n\n")
if __name__=="__main__":
    root=tk.Tk(); WeatherApp(root); root.mainloop()
