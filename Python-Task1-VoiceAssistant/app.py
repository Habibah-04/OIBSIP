import datetime as dt
import json
import os
import re
import smtplib
import threading
import webbrowser
from email.message import EmailMessage
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import requests
import pyttsx3
import speech_recognition as sr

APP = "OIBSIP Voice Assistant"
CONFIG_PATH = Path(__file__).with_name("config.json")

class AssistantApp:
    def __init__(self, root):
        self.root = root
        root.title(APP)
        root.geometry("820x650")
        root.minsize(700, 560)
        self.engine = None
        self.speech_lock = threading.Lock()
        self.recognizer = sr.Recognizer()
        self.reminders = []
        self.custom_commands = self.load_commands()
        self.style()
        self.build()
        self.say("Hello! I'm ready. Type a command or press Listen.")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def style(self):
        self.bg = "#0b1220"
        self.panel = "#121d30"
        self.fg = "#e7eef9"
        self.muted = "#9aabc4"
        self.root.configure(bg=self.bg)
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TFrame", background=self.bg)
        s.configure("Panel.TFrame", background=self.panel)
        s.configure("TLabel", background=self.bg, foreground=self.fg, font=("Segoe UI", 10))
        s.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#8be9d1")
        s.configure("Muted.TLabel", foreground=self.muted)
        s.configure("TButton", padding=9, font=("Segoe UI", 10, "bold"))
        s.configure("Accent.TButton", background="#39c6a6", foreground="#06121d")
        s.map("Accent.TButton", background=[("active", "#66e0c5")])

    def build(self):
        header = ttk.Frame(self.root, padding=(24, 22, 24, 10)); header.pack(fill="x")
        ttk.Label(header, text="VOICE ASSISTANT", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Speak naturally, set reminders, check weather, search the web.", style="Muted.TLabel").pack(anchor="w", pady=(4, 0))
        panel = ttk.Frame(self.root, style="Panel.TFrame", padding=16); panel.pack(fill="both", expand=True, padx=24, pady=12)
        self.log = tk.Text(panel, height=18, bg="#0e1727", fg=self.fg, insertbackground=self.fg,
                           relief="flat", wrap="word", font=("Consolas", 10), padx=12, pady=12)
        self.log.pack(fill="both", expand=True)
        row = ttk.Frame(self.root, padding=(24, 4, 24, 22)); row.pack(fill="x")
        self.command = tk.StringVar()
        entry = ttk.Entry(row, textvariable=self.command, font=("Segoe UI", 11))
        entry.pack(side="left", fill="x", expand=True, ipady=8); entry.bind("<Return>", lambda e: self.submit())
        ttk.Button(row, text="Run command", style="Accent.TButton", command=self.submit).pack(side="left", padx=8)
        ttk.Button(row, text="Listen", command=self.listen).pack(side="left")
        ttk.Button(row, text="Add command", command=self.add_command).pack(side="left", padx=(8, 0))
        self.log_msg("System", "Ready. Try: 'what time is it', 'search for Python decorators', 'remind me in 2 minutes to stretch'.")

    def log_msg(self, who, text):
        self.log.insert("end", f"{who}: {text}\n\n"); self.log.see("end")

    
    def say(self, text):
          """Display the response and queue its speech."""
          self.log_msg("Assistant", text)
          threading.Thread(
                  target=self._speak,
                  args=(text,),
                  daemon=True
          ).start()


    def _speak(self, text):
          """Speak responses sequentially using Windows SAPI5."""
          if not text or not str(text).strip():
                 return

          try:
                # Prevent two responses from speaking simultaneously.
                with self.speech_lock:
                        import pyttsx3

                        print(f"Assistant speaking: {text}")

                        engine = pyttsx3.init(driverName="sapi5")
                        engine.setProperty("volume", 1.0)
                        engine.setProperty("rate", 170)
                        engine.say(str(text))
                        engine.runAndWait()
                        engine.stop()

          except Exception as e:
                  print(f"Speech error: {e}")
    
    def load_commands(self):
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8")).get("custom_commands", {})
        except Exception:
            return {"open github": "https://github.com", "open youtube": "https://youtube.com"}

    def listen(self):
        def work():
            try:
                with sr.Microphone() as source:
                    self.root.after(0, lambda: self.log_msg("System", "Listening…"))
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                self.root.after(0, lambda: (self.command.set(text), self.submit()))
            except Exception as exc:
                self.root.after(0, lambda: self.say(f"I couldn't understand that or access the microphone. You can type instead. Details: {exc}"))
        threading.Thread(target=work, daemon=True).start()

    def submit(self):
        text = self.command.get().strip()
        if not text: return
        self.command.set(""); self.log_msg("You", text)
        self.handle(text)

    def handle(self, text):
        q = text.lower().strip()
        if q in self.custom_commands or q.startswith("open "):
            url = self.custom_commands.get(q)
            if not url and q in ("open google", "open youtube", "open github", "open gmail"):
                url = {"open google":"https://google.com","open youtube":"https://youtube.com","open github":"https://github.com","open gmail":"https://mail.google.com"}[q]
            if url:
                webbrowser.open(url); self.say(f"Opening {q.replace('open ', '')}."); return
        if any(x in q for x in ("hello", "hi assistant", "good morning", "good evening")):
            self.say("Hello! How can I help you?"); return
        if "time" in q:
            self.say("The time is " + dt.datetime.now().strftime("%I:%M %p")); return
        if "date" in q or "today" in q:
            self.say("Today is " + dt.datetime.now().strftime("%A, %d %B %Y")); return
        if q.startswith("search for ") or q.startswith("search "):
            query = re.sub(r"^search( for)?\s+", "", text, flags=re.I)
            webbrowser.open("https://www.google.com/search?q=" + requests.utils.quote(query))
            self.say("I opened a web search for " + query); return
        m = re.search(r"remind me in (\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?) to (.+)", q)
        if m:
            amount, unit, reminder = int(m.group(1)), m.group(2), m.group(3)
            factor = 3600 if unit.startswith(("hour","hr")) else 60 if unit.startswith(("minute","min")) else 1
            if amount < 1 or amount > 10080:
                self.say("Please choose a reminder duration between 1 and 10080 units."); return
            self.say(f"Reminder set for {amount} {unit}: {reminder}.")
            timer = threading.Timer(amount * factor, lambda: self.root.after(0, self.reminder_fired, reminder))
            timer.daemon = True; timer.start(); self.reminders.append(timer); return
        if q.startswith("weather in "):
            city = text[11:].strip()
            self.weather(city); return
        if q.startswith("send email to "):
            self.send_email(text); return
        if q.startswith("add command "):
            self.add_command(); return
        answers = {
            "what is python": "Python is a general-purpose programming language known for readable syntax and a large ecosystem.",
            "what is ai": "Artificial intelligence is the field of building systems that perform tasks associated with human intelligence.",
            "help": "Try: hello, time, date, search for a topic, weather in Lucknow, remind me in 2 minutes to stretch, or send email to address | subject | message."
        }
        for key, answer in answers.items():
            if key in q: self.say(answer); return
        self.say("I don't have a local answer for that yet. I can search the web if you say 'search for' followed by your topic.")

    def reminder_fired(self, text):
        self.say("Reminder: " + text)
        try: messagebox.showinfo("Reminder", text)
        except Exception: pass

    def weather(self, city):
        key = os.getenv("OPENWEATHER_API_KEY")
        if not key:
            self.say("Weather needs an OPENWEATHER_API_KEY environment variable. Add your key, restart the app, and try again."); return
        try:
            r = requests.get("https://api.openweathermap.org/data/2.5/weather", params={"q":city,"appid":key,"units":"metric"}, timeout=8)
            data = r.json()
            if r.status_code != 200: raise ValueError(data.get("message", "Weather request failed"))
            desc = data["weather"][0]["description"]
            self.say(f"In {data['name']}, it is {data['main']['temp']:.1f} degrees Celsius, {desc}, humidity {data['main']['humidity']} percent.")
        except Exception as e: self.say("I couldn't fetch the weather: " + str(e))

    def send_email(self, text):
        # Explicit format: send email to address | subject | message
        parts = text.split("|", 2)
        if len(parts) != 3:
            self.say("Use this format: send email to person@example.com | Subject | Message."); return
        recipient = parts[0][len("send email to "):].strip()
        host, sender, password = os.getenv("OIBSIP_SMTP_HOST"), os.getenv("OIBSIP_EMAIL"), os.getenv("OIBSIP_EMAIL_APP_PASSWORD")
        port = int(os.getenv("OIBSIP_SMTP_PORT", "587"))
        if not all((host, sender, password)):
            self.say("Email is not configured. Set OIBSIP_SMTP_HOST, OIBSIP_EMAIL and OIBSIP_EMAIL_APP_PASSWORD."); return
        try:
            msg = EmailMessage(); msg["Subject"] = parts[1].strip(); msg["From"] = sender; msg["To"] = recipient; msg.set_content(parts[2].strip())
            with smtplib.SMTP(host, port, timeout=10) as server:
                server.starttls(); server.login(sender, password); server.send_message(msg)
            self.say("Email sent successfully.")
        except Exception as e: self.say("Email could not be sent: " + str(e))

    def add_command(self):
        phrase = simpledialog.askstring("Custom command", "Command phrase (e.g. open portfolio):", parent=self.root)
        if not phrase: return
        url = simpledialog.askstring("Custom command", "Website URL to open:", parent=self.root)
        if not url or not url.startswith(("https://", "http://")):
            messagebox.showerror("Invalid URL", "Enter a URL beginning with http:// or https://"); return
        self.custom_commands[phrase.lower().strip()] = url
        try: CONFIG_PATH.write_text(json.dumps({"custom_commands": self.custom_commands}, indent=2), encoding="utf-8")
        except Exception as e: messagebox.showerror("Save failed", str(e)); return
        self.say(f"Custom command added: {phrase}")

    def close(self):
        for timer in self.reminders:
            try: timer.cancel()
            except Exception: pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    AssistantApp(root)
    root.mainloop()
