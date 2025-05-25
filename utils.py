import random
import string
import csv
from models import Bank, Account, User
 
def users_from_csv(csv_path):
    users = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                user = User.from_full_name(
                    row['user_full_name'],
                    birth_day=row.get('birth_day'),
                    accounts=row.get('accounts', "")
                )
                users.append(user)
            except Exception as e:
                print(f"Error validating row {row}: {e}")
    return users


def banks_from_csv(csv_path):
    banks = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                bank = Bank.from_name(row["name"])
                banks.append(bank)
            except Exception as e:
                print(f"Error validating row {row}: {e}")
    return banks


def accounts_from_csv(csv_path):
    accounts = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                account = Account(
                    user_id=int(row["user_id"]),
                    type=row["type"],
                    account_number=row["account_number"],
                    bank_id=int(row["bank_id"]),
                    currency=row["currency"],
                    amount=float(row["amount"]),
                    status=row["status"]
                )
                accounts.append(account)
            except Exception as e:
                print(f"Error validating row {row}: {e}")
    return accounts


def generate_account_number():
    prefix = "ID--"
    letters = ''.join(random.choices(string.ascii_letters, k=2))
    digits = ''.join(random.choices(string.digits, k=7))
    postfix = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    return f"{prefix}{letters}-{digits}-{postfix}"
