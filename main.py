import argparse
import sys
from pathlib import Path
from constants import DEFAULT_API_URL, DEFAULT_CSV_NAME
from io_utils import download_csv, load_csv, write_group_files, log_tree, archive_folder
from processing import filter_records, enrich_records, remove_pre1960, group_by_decade_country
from logger_config import configure_logging, get_logger


def parse_args():
    parser = argparse.ArgumentParser(description="Prepare randomuser data for analysis")
    
    parser.add_argument(
        "dest_folder",
        help="Output directory path"
    )
    parser.add_argument(
        "--filename",
        default=Path(DEFAULT_CSV_NAME).stem,
        help="Base name for CSV & log (default: data)"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--gender",
        choices=["male", "female"],
        help="Filter by gender"
    )
    group.add_argument(
        "--num_rows",
        type=int,
        help="Limit to first N rows"
    )
    parser.add_argument(
        "--log_level",
        default="INFO",
        choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],
        help="Logging level"
    )
    
    return parser.parse_args()


def initialize_logger(output_dir: Path, base_name: str, level: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / f"{base_name}.log"
    
    logger = get_logger(base_name)
    logger.setLevel(getattr(__import__('logging'), level))
    
    fh = __import__('logging').FileHandler(log_path, mode="w", encoding="utf-8")
    
    fmt = __import__('logging').Formatter("%(asctime)s — %(levelname)s — %(message)s")
    
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.info(f"Logger started at {level}")
    return logger


def main():
    args = parse_args()
    configure_logging(getattr(__import__('logging'), args.log_level))
    dest = Path(args.dest_folder)
    logger = initialize_logger(dest, args.filename, args.log_level)

    raw_csv = Path(f"{args.filename}.csv")
    download_csv(DEFAULT_API_URL, raw_csv, logger)

    records = load_csv(raw_csv, logger)
    records = filter_records(records, args.gender, args.num_rows, logger)
    records = enrich_records(records, logger)

    dest.mkdir(parents=True, exist_ok=True)
    moved_csv = dest / raw_csv.name
    raw_csv.replace(moved_csv)
    logger.info(f"Moved raw CSV to {moved_csv}")

    records = remove_pre1960(records, logger)
    grouped = group_by_decade_country(records, logger)
    write_group_files(dest, grouped, logger)

    logger.info(f"Directory structure under {dest}:")
    log_tree(dest, logger)
    archive_folder(dest, logger)


if __name__ == "__main__":
    sys.exit(main())
