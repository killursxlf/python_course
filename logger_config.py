import logging
from pathlib import Path

def configure_logging(level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def get_logger(name: str = __name__):
    return logging.getLogger(name)


def initialize_logger(output_dir: Path, base_name: str, level: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / f"{base_name}.log"

    logger = get_logger(base_name)
    logger.setLevel(getattr(logging, level))

    fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
    fh.setFormatter(fmt)

    logger.addHandler(fh)
    logger.info(f"Logger started at {level}")
    return logger
