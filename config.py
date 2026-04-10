import os
from datetime import date
from auth import viking_login, fitatu_login

def _load_env(path=".env"):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()

# Dzisiejsza data - cron odpala o 7:00
TARGET_DATES = [date.today().strftime("%Y-%m-%d")]

MEAL_MAPPING = {
    "\u015aniadanie": "breakfast",
    "II \u015bniadanie": "second_breakfast",
    "Obiad": "dinner",
    "Podwieczorek": "snack",
    "Kolacja": "supper",
}

_viking_headers, VIKING_ORDER_ID = viking_login(
    os.environ["VIKING_EMAIL"],
    os.environ["VIKING_PASSWORD"],
)

_fitatu_headers, FITATU_USER_ID = fitatu_login(
    os.environ["FITATU_EMAIL"],
    os.environ["FITATU_PASSWORD"],
    os.environ["FITATU_SECRET"],
)

VIKING_COOKIE        = _viking_headers["Cookie"]
FITATU_SECRET        = _fitatu_headers["Api-Secret"]
FITATU_AUTHORIZATION = _fitatu_headers["Authorization"]