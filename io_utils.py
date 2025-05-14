import csv
import shutil
from collections import Counter
from pathlib import Path
from urllib.request import urlopen


def download_csv(api_url: str, target_path: Path, logger) -> None:
    logger.info(f"Downloading CSV from {api_url}")
    
    with urlopen(api_url) as resp:
        data = resp.read().decode("utf-8")
        
    target_path.write_text(data, encoding="utf-8")
    logger.info(f"Saved CSV to {target_path}")


def load_csv(path: Path, logger) -> list[dict]:
    logger.info(f"Loading records from {path}")
    
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    logger.info(f"Loaded {len(rows)} records")
    return rows


def write_group_files(base_dir: Path, grouped: dict, logger) -> None:
    for decade, countries in grouped.items():
        ddir = base_dir / decade
        ddir.mkdir(parents=True, exist_ok=True)
        
        for country, recs in countries.items():
            cdir = ddir / country
            cdir.mkdir(exist_ok=True)
            
            ages = [int(r["dob.age"]) for r in recs]
            regs = [float(r["registered.age"]) for r in recs]
            
            max_age = max(ages) if ages else 0
            avg_reg = sum(regs) / len(regs) if regs else 0.0
            
            pop_id = Counter(r["id.name"] for r in recs).most_common(1)[0][0]
            fname = f"max_age_{max_age}_avg_registered_{avg_reg:.2f}_popular_id_{pop_id}.csv"
            out_path = cdir / fname
            
            with out_path.open("w", newline='', encoding="utf-8") as outf:
                writer = csv.DictWriter(outf, fieldnames=recs[0].keys())
                writer.writeheader()
                writer.writerows(recs)
                
            logger.info(f"Wrote {len(recs)} rows to {out_path}")


def log_tree(folder: Path, logger, indent: int = 0) -> None:
    for entry in sorted(folder.iterdir()):
        flag = "[D]" if entry.is_dir() else "[F]"
        logger.info(f"{'    '*indent}{entry.name} {flag}")
        
        if entry.is_dir():
            log_tree(entry, logger, indent+1)


def archive_folder(folder: Path, logger) -> Path:
    path = shutil.make_archive(str(folder), 'zip', root_dir=str(folder))
    logger.info(f"Created archive at {path}")
    return Path(path)
