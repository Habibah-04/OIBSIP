# Task 1 — Voice Assistant (Advanced)

A Tkinter desktop assistant with speech recognition and speech output, natural-language-ish intent parsing, time/date, web search, reminders, weather lookup, a small offline knowledge base, configurable custom commands, and optional email sending.

## Run
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy config.example.json config.json
python app.py
```
If PyAudio fails to install on Windows, install a compatible wheel for your Python version or use the **Type command** field; text commands work without a microphone. `SpeechRecognition` Google recognition requires internet.

## Optional settings
Set `OPENWEATHER_API_KEY` for weather. For email, set `OIBSIP_SMTP_HOST`, `OIBSIP_SMTP_PORT` (default 587), `OIBSIP_EMAIL`, and `OIBSIP_EMAIL_APP_PASSWORD` as environment variables. Use a test mailbox/app password, never your normal account password. The assistant only sends email when the user explicitly types a `send email to ... | subject | message` command.

## Privacy
Microphone audio is captured only after pressing Listen. Speech recognition through Google's recognizer sends audio to that service for transcription. Weather queries send the requested city to OpenWeatherMap. Email text is sent through the configured SMTP provider only when the user requests sending. Reminder text and custom commands remain local. Do not enter confidential information.
