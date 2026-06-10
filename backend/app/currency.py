"""Static FX rates for reporting only. Salaries are stored in local currency."""

USD_TO_LOCAL: dict[str, float] = {
    "USD": 1.0,
    "GBP": 0.79,
    "EUR": 0.92,
    "INR": 83.5,
    "CAD": 1.36,
    "AUD": 1.53,
    "JPY": 149.0,
    "BRL": 4.95,
    "SGD": 1.34,
    "SEK": 10.5,
}

COUNTRY_CURRENCY: dict[str, str] = {
    "United States": "USD",
    "United Kingdom": "GBP",
    "Germany": "EUR",
    "France": "EUR",
    "India": "INR",
    "Canada": "CAD",
    "Australia": "AUD",
    "Japan": "JPY",
    "Brazil": "BRL",
    "Singapore": "SGD",
    "Netherlands": "EUR",
    "Sweden": "SEK",
}


def local_to_usd(amount: float, currency: str) -> float:
    rate = USD_TO_LOCAL.get(currency, 1.0)
    if rate == 0:
        return amount
    return amount / rate


def usd_to_local(amount: float, currency: str) -> float:
    rate = USD_TO_LOCAL.get(currency, 1.0)
    return amount * rate
