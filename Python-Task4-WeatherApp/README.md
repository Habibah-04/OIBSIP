# Task 4 — Weather App (Advanced)

Tkinter weather dashboard with current conditions, weather icon, hourly forecast for approximately the next six hours, daily summaries for five days, Celsius/Fahrenheit toggle, and in-GUI error messages.

## Setup
1. Create an API key at https://openweathermap.org/api.
2. Set it in PowerShell for the current terminal:
   ```powershell
   $env:OPENWEATHER_API_KEY="YOUR_API_KEY_HERE"
   ```
3. Run:
   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```
The API key is read from the environment and must not be committed. Forecast availability and quota depend on your OpenWeatherMap account/API plan. The app does not perform IP-based location detection; enter a city manually to avoid transmitting location without a deliberate action.
