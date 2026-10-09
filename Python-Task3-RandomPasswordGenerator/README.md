# Task 3 — Random Password Generator (Advanced)

A desktop password generator using Python's cryptographically secure `secrets` module. Features include length control, character-set checkboxes, mandatory coverage of every selected character type, strength indicator, ambiguous-character exclusion, clipboard copy, and in-session-only history of the last five generated passwords.

## Run
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
History is intentionally not saved to disk. Clipboard integration can depend on your desktop environment; if it fails, select and copy the displayed password manually.
