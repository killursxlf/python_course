from logging_config import get_logger

logger = get_logger("api")

def api_response(success: bool, message: str, status_code: int = 200, log_type: str = "info"):
    log_func = getattr(logger, log_type, logger.info)
    log_func(f"[{status_code}] {message}")
    return {
        "success": success,
        "message": message,
        "status_code": status_code
    }
