import os
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image, ImageTk

BG = "#0b1220"
CARD = "#142136"
TEXT = "#e7eef9"
MUTED = "#9aabc4"
ACCENT = "#35d0b0"

API = "https://api.openweathermap.org/data/2.5"
ICON_API = "https://openweathermap.org/img/wn/{}@2x.png"


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Atmos | Weather Dashboard")
        self.root.geometry("940x740")
        self.root.minsize(760, 640)
        self.root.configure(bg=BG)

        self.unit = tk.StringVar(value="Celsius")
        self.city = tk.StringVar(value="Lucknow")
        self.status = tk.StringVar(
            value="Enter a city and fetch current conditions."
        )

        self.data = None
        self.icon_img = None
        self.request_in_progress = False
        self.icon_request_id = 0

        self.build()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def build(self):
        tk.Label(
            self.root,
            text="ATMOS",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 25, "bold"),
        ).pack(anchor="w", padx=28, pady=(20, 0))

        tk.Label(
            self.root,
            text="WEATHER DASHBOARD  /  CURRENT + FORECAST",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=29, pady=(2, 15))

        search = tk.Frame(self.root, bg=CARD, padx=16, pady=14)
        search.pack(fill="x", padx=26)

        self.city_entry = tk.Entry(
            search,
            textvariable=self.city,
            font=("Segoe UI", 12),
            bg="#0e1727",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
        )
        self.city_entry.pack(
            side="left", fill="x", expand=True, ipady=10
        )
        self.city_entry.bind("<Return>", lambda event: self.fetch())

        self.fetch_button = tk.Button(
            search,
            text="Get Weather",
            command=self.fetch,
            bg=ACCENT,
            fg="#06121d",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            cursor="hand2",
        )
        self.fetch_button.pack(side="left", padx=10)

        self.unit_box = ttk.Combobox(
            search,
            textvariable=self.unit,
            values=("Celsius", "Fahrenheit"),
            state="readonly",
            width=12,
        )
        self.unit_box.pack(side="left")
        self.unit.trace_add("write", lambda *_: self.redraw())

        self.current = tk.Frame(
            self.root, bg=CARD, padx=22, pady=18
        )
        self.current.pack(fill="x", padx=26, pady=14)

        self.big = tk.Label(
            self.current,
            text="—",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 34, "bold"),
        )
        self.big.pack(side="left", padx=(0, 22))

        self.icon_label = tk.Label(
            self.current,
            text="☁",
            bg=CARD,
            fg="#FFD166",
            font=("Segoe UI Emoji", 34),
            width=3,
        )
        self.icon_label.pack(side="left", padx=8)

        self.details = tk.Label(
            self.current,
            text="Current weather will appear here.",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 12),
            justify="left",
            anchor="w",
        )
        self.details.pack(side="left", padx=18)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(
            fill="both", expand=True, padx=26, pady=(0, 8)
        )

        self.hour_frame = tk.Frame(self.tabs, bg=BG)
        self.day_frame = tk.Frame(self.tabs, bg=BG)

        self.tabs.add(self.hour_frame, text="Next 6 hours")
        self.tabs.add(self.day_frame, text="5-day outlook")

        self.hour_text = tk.Text(
            self.hour_frame,
            bg=BG,
            fg=TEXT,
            relief="flat",
            font=("Consolas", 11),
            wrap="word",
            padx=16,
            pady=16,
            state="disabled",
        )
        self.hour_text.pack(fill="both", expand=True)

        self.day_text = tk.Text(
            self.day_frame,
            bg=BG,
            fg=TEXT,
            relief="flat",
            font=("Consolas", 11),
            wrap="word",
            padx=16,
            pady=16,
            state="disabled",
        )
        self.day_text.pack(fill="both", expand=True)

        tk.Label(
            self.root,
            textvariable=self.status,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
            anchor="w",
            wraplength=880,
        ).pack(anchor="w", padx=28, pady=(0, 14))

    def fetch(self):
        city = self.city.get().strip()

        if not city:
            self.status.set("Please enter a city name.")
            return

        key = os.getenv("OPENWEATHER_API_KEY", "").strip()

        if not key:
            self.status.set(
                "Missing OPENWEATHER_API_KEY. Set it in CMD and "
                "restart the app."
            )
            return

        if self.request_in_progress:
            self.status.set("A weather request is already in progress.")
            return

        self.request_in_progress = True
        self.fetch_button.config(state="disabled")
        self.status.set(f"Fetching weather for {city}...")

        threading.Thread(
            target=self._fetch,
            args=(city, key),
            daemon=True,
        ).start()

    def _fetch(self, city, key):
        try:
            current_response = requests.get(
                API + "/weather",
                params={
                    "q": city,
                    "appid": key,
                    "units": "metric",
                },
                timeout=12,
            )

            self._check_response(current_response)

            forecast_response = requests.get(
                API + "/forecast",
                params={
                    "q": city,
                    "appid": key,
                    "units": "metric",
                },
                timeout=12,
            )

            self._check_response(forecast_response)

            data = {
                "current": current_response.json(),
                "forecast": forecast_response.json(),
            }

            self.root.after(0, lambda result=data: self.show(result))

        except Exception as exc:
            error_message = str(exc)
            print(f"Weather request failed: {error_message}")

            try:
                self.root.after(
                    0,
                    lambda message=error_message: self.show_error(message),
                )
            except tk.TclError:
                pass

    @staticmethod
    def _check_response(response):
        if response.status_code == 200:
            return

        try:
            message = response.json().get(
                "message", "Request failed"
            )
        except (ValueError, requests.RequestException):
            message = f"HTTP {response.status_code}"

        raise ValueError(
            f"API error {response.status_code}: {message}"
        )

    def show_error(self, message):
        self.request_in_progress = False

        try:
            self.fetch_button.config(state="normal")
            self.status.set(f"Could not load weather: {message}")
        except tk.TclError:
            pass

    def show(self, data):
        self.request_in_progress = False
        self.fetch_button.config(state="normal")

        self.data = data
        self.redraw()

        self.status.set(
            f"Updated {datetime.now().strftime('%H:%M:%S')} "
            "• Forecasts are API estimates."
        )

    def temp(self, celsius):
        if self.unit.get() == "Fahrenheit":
            return celsius * 9 / 5 + 32
        return celsius

    def set_text(self, widget, content):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", content)
        widget.config(state="disabled")

    def redraw(self):
        if not self.data:
            return

        current = self.data["current"]
        forecast = self.data["forecast"]
        main = current["main"]
        weather = current["weather"][0]

        unit = "°C" if self.unit.get() == "Celsius" else "°F"

        self.big.config(
            text=f"{self.temp(main['temp']):.1f}{unit}"
        )

        self.details.config(
            text=(
                f"{current['name']}, "
                f"{current['sys'].get('country', '')}\n"
                f"{weather['description'].title()}\n"
                f"Humidity  {main['humidity']}%     "
                f"Wind  {current.get('wind', {}).get('speed', 0)} m/s\n"
                f"Feels like "
                f"{self.temp(main['feels_like']):.1f}{unit}     "
                f"High/Low "
                f"{self.temp(main['temp_max']):.1f}/"
                f"{self.temp(main['temp_min']):.1f}{unit}"
            )
        )

        # Show a visible fallback while the online icon loads.
        self.icon_label.config(
            image="",
            text=self._weather_symbol(weather),
            fg=self._symbol_color(weather),
            font=("Segoe UI Emoji", 34),
        )
        self.icon_img = None

        # Each icon request gets an ID so an old result cannot replace
        # the icon for a newer city search.
        self.icon_request_id += 1
        request_id = self.icon_request_id

        threading.Thread(
            target=self._load_icon,
            args=(weather.get("icon", ""), request_id),
            daemon=True,
        ).start()

        # Next six forecast entries (usually three-hour intervals).
        hourly_lines = []

        for item in forecast.get("list", [])[:6]:
            timestamp = datetime.fromtimestamp(item["dt"])
            description = item["weather"][0]["description"].title()
            temperature = self.temp(item["main"]["temp"])

            hourly_lines.append(
                f"{timestamp.strftime('%a %H:%M'):<16} "
                f"{temperature:>5.1f}{unit}   "
                f"{description:<22} "
                f"Humidity {item['main']['humidity']}%"
            )

        self.set_text(
            self.hour_text,
            "\n\n".join(hourly_lines) or "No forecast data available.",
        )

        # Group forecast entries by local calendar day.
        groups = {}

        for item in forecast.get("list", []):
            day = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            groups.setdefault(day, []).append(item)

        daily_lines = []

        for day, items in list(groups.items())[:5]:
            temperatures = [
                self.temp(item["main"]["temp"]) for item in items
            ]

            midday = min(
                items,
                key=lambda item: abs(
                    datetime.fromtimestamp(item["dt"]).hour - 12
                ),
            )

            description = midday["weather"][0]["description"].title()
            day_label = datetime.strptime(
                day, "%Y-%m-%d"
            ).strftime("%A, %d %b")

            daily_lines.append(
                f"{day_label}\n"
                f"  {min(temperatures):.1f}{unit} — "
                f"{max(temperatures):.1f}{unit}   •   {description}"
            )

        self.set_text(
            self.day_text,
            "\n\n".join(daily_lines) or "No daily forecast available.",
        )

    @staticmethod
    def _weather_symbol(weather):
        description = weather.get("main", "").lower()

        if description == "clear":
            return "☀"
        if description == "clouds":
            return "☁"
        if description == "rain":
            return "🌧"
        if description == "drizzle":
            return "🌦"
        if description == "thunderstorm":
            return "⛈"
        if description == "snow":
            return "❄"
        if description in ("mist", "smoke", "haze", "dust", "fog", "sand", "ash"):
            return "🌫"
        if description == "squall":
            return "💨"
        if description == "tornado":
            return "🌪"

        return "🌤"

    @staticmethod
    def _symbol_color(weather):
        description = weather.get("main", "").lower()

        if description == "clear":
            return "#FFD166"
        if description in ("rain", "drizzle", "thunderstorm"):
            return "#78BFFF"
        if description == "snow":
            return "#E7EEF9"
        return "#A8BED8"

    def _load_icon(self, icon_code, request_id):
        if not icon_code:
            return

        try:
            url = ICON_API.format(icon_code)
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            image = Image.open(
                BytesIO(response.content)
            ).convert("RGBA")
            image = image.resize(
                (80, 80),
                Image.Resampling.LANCZOS,
            )

            # Create Tkinter image on the GUI thread.
            self.root.after(
                0,
                lambda img=image, rid=request_id: self._set_icon(img, rid),
            )

        except Exception as exc:
            print(f"Weather icon unavailable: {exc}")
            # The descriptive Unicode symbol remains visible as fallback.

    def _set_icon(self, image, request_id):
        if request_id != self.icon_request_id:
            return

        try:
            photo = ImageTk.PhotoImage(image)
            self.icon_img = photo
            self.icon_label.config(image=photo, text="")
        except tk.TclError:
            pass

    def close(self):
        self.icon_request_id += 1
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
