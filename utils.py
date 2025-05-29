import random
import string
import csv
from typing import  Callable, List, Tuple, Any
from models import Bank, Account, User
 

def generate_account_number():
    prefix = "ID--"
    letters = ''.join(random.choices(string.ascii_letters, k=2))
    digits = ''.join(random.choices(string.digits, k=7))
    postfix = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    return f"{prefix}{letters}-{digits}-{postfix}"


def objects_from_csv(
    csv_path: str,
    row_parser: Callable[[dict], Any],
    logger=None
) -> Tuple[List[Any], List[dict]]:
    """
    Reads and validates objects from CSV file using a custom parser for each row.

    
        :params csv_path (str): path to CSV file
        :params row_parser (callable): function to convert a CSV row dict to a dataclass instance
        :params logger: optional logger

        :return: Tuple of (valid_objs: list, errors: list[dict])
    """
    objects = []
    errors = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            try:
                obj = row_parser(row)
                objects.append(obj)
            except Exception as e:
                if logger:
                    logger.error(f"Row {i} skipped: {e} — {row}")
                errors.append({"row_num": i, "error": str(e), "row": row})
    return objects, errors


def user_row_parser(row):
    return User.built_from_dict(row)


def bank_row_parser(row):
    return Bank.built_from_dict(row)


def account_row_parser(row):
    return Account.built_from_dict(row)
    