# A-to-Z GitHub upload guide (Windows)

## A. Prepare your repository
1. Open `https://github.com/Habibah-04/OIBSIP` (or your own OIBSIP repository).
2. Confirm the repository name is **OIBSIP** and you have write access.
3. Download and extract the provided ZIP on your computer.
4. Open the extracted `OIBSIP_Python_Advanced_Tasks` folder. It contains the five task folders.

## B. Copy the five folders into the repository
The final layout should look like:
```text
OIBSIP/
├── README.md
├── GITHUB_UPLOAD_GUIDE.md
├── Python-Task1-VoiceAssistant/
├── Python-Task2-BMICalculator/
├── Python-Task3-RandomPasswordGenerator/
├── Python-Task4-WeatherApp/
└── Python-Task5-ChatApplication/
```
If your repository already contains `Python-Task1-VoiceAssistant`, keep it if it is your current working version and merge carefully. Do not create a nested `OIBSIP/OIBSIP/...` folder. The task folders must sit at the repository root.

## C. Open PowerShell in the repository root
In File Explorer, open the `OIBSIP` local folder, click the address bar, type `powershell`, and press Enter. Check:
```powershell
git status
git remote -v
```
If this is not yet a Git repository:
```powershell
git init
git branch -M main
git remote add origin https://github.com/Habibah-04/OIBSIP.git
```
If `origin` already exists, do not add it again. Check it with `git remote -v`. To correct the URL:
```powershell
git remote set-url origin https://github.com/Habibah-04/OIBSIP.git
```

## D. Review before staging
```powershell
git status --short
```
Make sure no `.venv`, `config.json`, `.env`, API key, SMTP password, personal password, or database containing personal data is included. `.gitignore` files exclude common local secrets/databases.

## E. Stage, commit and push all five task folders
```powershell
git add README.md GITHUB_UPLOAD_GUIDE.md .gitignore Python-Task1-VoiceAssistant Python-Task2-BMICalculator Python-Task3-RandomPasswordGenerator Python-Task4-WeatherApp Python-Task5-ChatApplication
git status
git commit -m "Add five advanced Python internship tasks"
git push -u origin main
```
If Git says `nothing to commit`, check `git status` and verify you copied the folders into the repository root. If Git reports a non-fast-forward rejection because GitHub already has a README or commits, first run:
```powershell
git pull --rebase origin main
git push -u origin main
```
If conflicts appear, resolve them before continuing; don't blindly force-push.

## F. Verify on GitHub
Refresh `https://github.com/Habibah-04/OIBSIP`. Confirm all five folders are visible and each has `app.py` or its relevant scripts, `README.md`, and `requirements.txt`.

## G. Test each task before recording your demo
- Task 1: run `python app.py`; test typed hello/time/search/reminder and microphone only if configured.
- Task 2: calculate a BMI, save a named record, refresh, and view the trend.
- Task 3: select at least two character sets, generate, test clipboard, and verify history only lasts for the session.
- Task 4: set `OPENWEATHER_API_KEY`, fetch a real city, switch units, and inspect both forecast tabs.
- Task 5: run `python server.py`, then start two separate `python client.py` processes; register two accounts and exchange messages in a room.

## H. Internship submission checklist
Use the task guide's required naming format. Make a separate demo video for each task with a 2-second title card: full name, Python Programming track, and task title. Show the app working end-to-end. Post/link the demo on LinkedIn, tag Oasis Infobyte, include `#oasisinfobyte` and relevant hashtags, comment substantively on at least two peers' demo videos, and submit the OIBSIP repository URL in the official form shared by your cohort. The guide says Python interns need at least three tasks; this package includes all five, but you still need to run/test them yourself.
