# FoodForScotland

A website that helps tackle hunger in Scotland by letting people donate to
local food banks and sign up to volunteer for deliveries.

## Features (in progress)

- Browse food banks and donate to a chosen one
- Sign up as a volunteer
- Claim open delivery requests to get donated food to a food bank

## Project structure

```
ADAhack2026/
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── models/__init__.py # SQLAlchemy models (FoodBank, Donation, Volunteer, DeliveryRequest)
│   ├── routes/             # Blueprints: main, donations, volunteers
│   ├── templates/          # Jinja2 HTML templates
│   └── static/             # CSS and JS
├── instance/                # Local SQLite DB (gitignored)
├── tests/
├── config.py
├── run.py
└── requirements.txt
```

## Getting started

```bash
python -m venv .venv
source .venv/Scripts/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Then visit http://127.0.0.1:5000

## Next steps

- Seed some real Scottish food banks into the database
- Add a map view of food banks
- Add authentication for volunteers
- Hook up real payments for donations
