import re
from constants import (DEFAULT_REG_FORMAT)
from datetime import timedelta, timezone, datetime


def parse_timezone_offset(offset_str: str) -> timezone:
    match = re.match(r"^([+-])(\d{1,2}):?(\d{2})?$", offset_str)
    
    if not match:
        return timezone.utc
    
    sign = 1 if match.group(1) == "+" else -1
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    
    return timezone(sign * timedelta(hours=hours, minutes=minutes))


def normalize_iso_datetime(iso_str: str) -> str:
    return datetime.fromisoformat(iso_str).strftime(DEFAULT_REG_FORMAT)
