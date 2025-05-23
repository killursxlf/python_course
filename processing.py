from datetime import datetime, timezone
from constants import (FIELD_DOB, FIELD_REGISTERED_DATE, FIELD_TIMEZONE_OFFSET, TITLE_MAP, FIELD_TITLE, 
                        DEFAULT_BIRTH_FORMAT, DEFAULT_REG_FORMAT, FIELD_GLOBAL_INDEX, FIELD_CURRENT_TIME)
from datetime_utils import parse_timezone_offset, normalize_iso_datetime


def filter_records(records: list[dict], gender: str | None, limit: int | None, logger) -> list[dict]:
    original = len(records)
    
    if gender:
        records = [r for r in records if r.get("gender", "").lower() == gender]
        logger.info(f"Filtered by gender={gender}: {original}→{len(records)}")
        
    elif limit:
        records = records[:limit]
        logger.info(f"Limited to first {limit} rows: {original}→{len(records)}")
        
    return records


def enrich_records(records: list[dict], logger) -> list[dict]:
    now_utc = datetime.now(timezone.utc)
    enriched = []
    
    for i, r in enumerate(records, 1):
        r[FIELD_GLOBAL_INDEX] = i
        
        tz = parse_timezone_offset(r.get(FIELD_TIMEZONE_OFFSET, '+0:00'))
        local_dt = now_utc.astimezone(tz)
        r[FIELD_CURRENT_TIME] = local_dt.strftime(DEFAULT_REG_FORMAT)

        orig_title = r.get(FIELD_TITLE, '')
        r[FIELD_TITLE] = TITLE_MAP.get(orig_title, orig_title)

        dclean = normalize_iso_datetime(r.get(FIELD_DOB, ''))
        dob = datetime.strptime(dclean, DEFAULT_REG_FORMAT)
        r[FIELD_DOB] = dob.strftime(DEFAULT_BIRTH_FORMAT)
        
        rclean = normalize_iso_datetime(r.get(FIELD_REGISTERED_DATE, ''))
        reg = datetime.strptime(rclean, DEFAULT_REG_FORMAT)
        r[FIELD_REGISTERED_DATE] = reg.strftime("%m-%d-%Y, %H:%M:%S")

        enriched.append(r)
        
    logger.info(f"Enriched {len(enriched)} records")
    return enriched


def remove_pre1960(records: list[dict], logger) -> list[dict]:
    filtered = list(filter(lambda r: int(r[FIELD_DOB].split('/')[-1]) >= 1960, records))
    
    logger.info(f"Removed {len(records) - len(filtered)} pre-1960")
    return filtered


def group_by_decade_country(records: list[dict], logger) -> dict[str, dict[str, list[dict]]]:
    grouped: dict[str, dict[str, list[dict]]] = {}
    
    for r in records:
        _, _, y = map(int, r[FIELD_DOB].split('/'))
        decade = f"{(y // 10) * 10}-th"
        country = r.get("location.country", "Unknown")
        grouped.setdefault(decade, {}).setdefault(country, []).append(r)
        
    logger.info("Grouped by decade and country")
    return grouped
