
# OIBSIP — Python Programming (Advanced Tier)

This repository contains five separate, runnable Python projects based on the **Python Programming** section of the OASIS INFOBYTE — SIP Task List:

1. `Python-Task1-VoiceAssistant`
2. `Python-Task2-BMICalculator`
3. `Python-Task3-RandomPasswordGenerator`
4. `Python-Task4-WeatherApp`
5. `Python-Task5-ChatApplication`

Each project includes its own README, requirements file, configuration example where needed, and source code. The applications use Tkinter GUIs; SQLite is used for local history where appropriate.

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

## GitHub upload
1. Create or open your repository named exactly `OIBSIP`.
2. Put these five task folders directly inside the repository root (alongside this root README).
3. In PowerShell, from the repository root:
```powershell
git status
git add README.md Python-Task1-VoiceAssistant Python-Task2-BMICalculator Python-Task3-RandomPasswordGenerator Python-Task4-WeatherApp Python-Task5-ChatApplication
git commit -m "Add five advanced Python internship tasks"
git push origin main
```
If your default branch is `master`, use `git push origin master`. Never upload `.venv`, API keys, passwords, or other secrets. Each task has a `.gitignore`.

## Internship checklist from the supplied task list
The guide says Python Programming interns must complete **at least 3 of the 5 tasks**; each task has Beginner and Advanced tiers. It also calls for source code + README + relevant screenshots/output, a demo video with a 2-second title card showing full name, track and task title, a LinkedIn post tagging Oasis Infobyte with `#oasisinfobyte`, substantive comments on two peers' demo videos, and submission through the form shared by the cohort. Completing all five is optional beyond the stated minimum, but makes a broader portfolio.

## Important notes
- API/network features need internet access and valid credentials.
- No credentials are included. Add your own locally via environment variables.
- Verify all apps on your own machine and take genuine screenshots/demo recordings before submitting; don't claim a feature worked unless you tested it.
