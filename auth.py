import requests
import logging
import base64
import json
from datetime import date

# ── Viking ───────────────────────────────────────────────────────────────────

VIKING_LOGIN_URL = "https://panel.kuchniavikinga.pl/api/auth/login"
VIKING_ORDER_LIST_URL = "https://panel.kuchniavikinga.pl/api/company/customer/order/all"


def viking_login(email: str, password: str) -> tuple[dict, int]:
    """Loguje się do Viking, zwraca (headers, order_id)."""
    session = requests.Session()

    resp = session.post(
        VIKING_LOGIN_URL,
        data={"username": email, "password": password},
        headers={
            "company-id": "kuchniavikinga",
            "x-launcher-type": "BROWSER_PANEL",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=30,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Viking login failed: {resp.status_code} {resp.text}")

    cookie_header = "; ".join(f"{k}={v}" for k, v in session.cookies.items())
    headers = {"Cookie": cookie_header}

    orders_resp = session.get(VIKING_ORDER_LIST_URL, headers=headers, timeout=30)
    if orders_resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch Viking orders: {orders_resp.status_code}")

    data = orders_resp.json()
    orders = data if isinstance(data, list) else [data]

    if not orders:
        raise RuntimeError("No Viking orders found")

    today = date.today().strftime("%Y-%m-%d")

    # Wybierz zamówienie którego zakres dat obejmuje dzisiaj
    current = next(
        (o for o in orders if o.get("dateFrom", "") <= today <= o.get("dateTo", "")),
        None
    )

    # Jeśli nie ma aktywnego dziś - weź najbliższe przyszłe
    if not current:
        future = [o for o in orders if o.get("dateFrom", "") > today]
        current = min(future, key=lambda o: o.get("dateFrom", "")) if future else None

    # Ostateczny fallback - najnowsze
    if not current:
        current = max(orders, key=lambda o: o.get("dateFrom", ""))

    order_id = current["orderId"]
    logging.info(f"Viking login OK, order_id={order_id}, dateFrom={current.get('dateFrom')}, dateTo={current.get('dateTo')}")
    return headers, order_id


# ── Fitatu ───────────────────────────────────────────────────────────────────

FITATU_LOGIN_URL = "https://pl-pl.fitatu.com/api/login"

FITATU_BASE_HEADERS = {
    "Api-Key": "FITATU-MOBILE-APP",
    "Api-Cluster": "pl-pl14208",
    "App-Os": "FITATU-WEB",
    "App-Locale": "pl_PL",
    "App-Timezone": "Europe/Warsaw",
    "App-Version": "4.5.11",
    "App-Uuid": "64c2d1b0-c8ad-11e8-8956-0242ac120008",
    "App-SearchLocale": "pl_PL",
    "App-StorageLocale": "pl_PL",
    "App-Location-Country": "UNKNOWN",
    "Accept": "application/json; version=v3",
    "Content-Type": "application/json",
}


def _decode_jwt_payload(token: str) -> dict:
    """Dekoduje payload z JWT bez weryfikacji podpisu."""
    payload = token.split(".")[1]
    payload += "=" * (4 - len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


def fitatu_login(email: str, password: str, api_secret: str) -> tuple[dict, str]:
    """Loguje się do Fitatu, zwraca (headers, user_id)."""
    login_headers = {**FITATU_BASE_HEADERS, "Api-Secret": api_secret}

    resp = requests.post(
        FITATU_LOGIN_URL,
        json={"_username": email, "_password": password},
        headers=login_headers,
        timeout=30,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Fitatu login failed: {resp.status_code} {resp.text}")

    data = resp.json()
    token = data["token"]

    jwt_payload = _decode_jwt_payload(token)
    user_id = jwt_payload["id"]

    headers = {
        **FITATU_BASE_HEADERS,
        "Api-Secret": api_secret,
        "Api-Cluster": f"pl-pl{user_id}",
        "Authorization": f"Bearer {token}",
    }

    logging.info(f"Fitatu login OK, user_id={user_id}")
    return headers, user_id
