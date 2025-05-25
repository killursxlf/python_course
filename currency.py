import requests
from config import CURRENCY_API_KEY, CURRENCY_API_URL, CURRENCY_API_TIMEOUT
from logging_config import get_logger

logger = get_logger("currency")

def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    if from_currency == to_currency:
        return 1.0
    
    headers = {"apikey": CURRENCY_API_KEY}
    params = {"base_currency": from_currency, "currencies": to_currency}
    
    try:
        resp = requests.get(CURRENCY_API_URL, headers=headers, params=params, timeout=CURRENCY_API_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        
        if "data" in data and to_currency in data["data"]:
            rate = data["data"][to_currency]
            logger.info(f"Exchange rate {from_currency} -> {to_currency} = {rate}")
            return float(rate)
        
        else:
            raise RuntimeError(f"No rate found for {from_currency}->{to_currency}")
        
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            logger.error("API limit exceeded!")
            raise RuntimeError("API limit exceeded!")
        
        logger.error(f"HTTP error: {e}")
        raise
    
    except Exception as e:
        logger.error(f"Currency API error: {e}")
        raise
