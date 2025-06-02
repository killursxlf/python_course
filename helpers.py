from logging_config import get_logger
import sys
import os

logger = get_logger("api")

def api_response(success: bool, message: str, status_code: int = 200, log_type: str = "info"):

    in_pytest = "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ

    if not in_pytest:
        log_func = getattr(logger, log_type, logger.info)
        log_func(f"[{status_code}] {message}")

    return {
        "success": success,
        "message": message,
        "status_code": status_code
    }
