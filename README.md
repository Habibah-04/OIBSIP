
# OIBSIP — Python Programming (Advanced Tier)

This repository contains five separate, runnable Python projects based on the **Python Programming** section of the OASIS INFOBYTE — SIP Task List:

1. `Python-Task1-VoiceAssistant`
2. `Python-Task2-BMICalculator`
3. `Python-Task3-RandomPasswordGenerator`
4. `Python-Task4-WeatherApp`
5. `Python-Task5-ChatApplication`

Each project includes its own README, requirements file, source code and output. 

## Requirements
- Python 3.10+ recommended (Python 3.13 should generally work).
- Windows instructions are included below; macOS/Linux are similar.
- Install dependencies separately inside each project virtual environment.

## Run any project (Windows PowerShell)
```powershell
cd Python-Task2-BMICalculator
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Repeat for each folder. For Python 3.10+ replace `py -3.13` with `py -3.10` or `python`.

## Task-specific setup
- **Voice Assistant:** microphone support depends on OS/audio drivers. Configure email and weather credentials only if you want those features. Do not commit secrets.
- **BMI Calculator:** records are saved in `bmi_history.db` in the project folder.
- **Password Generator:** uses Python's `secrets` module. Password history is kept in memory only and is never written to disk.
- **Weather App:** create a free OpenWeather API key and set `OPENWEATHER_API_KEY` as an environment variable. Forecast features use OpenWeatherMap's 5-day/3-hour forecast endpoint.
- **Chat Application:** start the server first, then run clients. Default server is `127.0.0.1:5055`; change host to `0.0.0.0` only when you understand network exposure. This demo uses local username/password authentication and is intended for learning, not public internet deployment.
