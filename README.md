# Hope Medical Demo

Quick local demo of a Flask backend + static frontend for booking appointments.

Requirements
- Python 3.8+
- MySQL server (local) with a database named `medical_db`.

Install dependencies

```bash
python -m pip install -r requirements.txt
```

Run the app

```bash
python app.py
```

Open in browser
- Visit `login.html` to sign up or log in.
- After login you'll be redirected to `index.html` to book appointments.

Database notes
- The app will auto-create `users` and `appointments` tables if they don't exist.
- Make sure `app.py` contains the correct MySQL credentials.
