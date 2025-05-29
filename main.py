from utils import objects_from_csv, user_row_parser
from api import add_users, add_banks, add_accounts, transfer_money
from analytics import (
    user_transactions_last_3_months,
    delete_incomplete_users_and_accounts,
    bank_with_most_active_users,
    bank_with_oldest_client,
    bank_with_biggest_capital,
    get_users_with_debt,
    assign_random_discounts,
)
from models import Bank
from logging_config import get_logger, setup_logging

def main():
    setup_logging()
    logger = get_logger("main-test")

    print("\n=== USERS FROM CSV ===")
    users, user_errors = objects_from_csv("users.csv", user_row_parser, logger)
    for err in user_errors:
        print(f"[USER ERROR] Row {err['row_num']}: {err['error']}")
    print(add_users(*users))

    print("\n=== ADD BANKS ===")
    bank1 = Bank(name="Central Bank")
    bank2 = Bank(name="Second Bank")
    print(add_banks(bank1))
    print(add_banks(bank2))

    print("\n=== ADD ACCOUNTS FROM LIST ===")
    account_dicts = [
        {"user_id": 1, "type": "debit", "account_number": "ID--j3-q-432547-u9", "bank_id": 1, "currency": "USD", "amount": 1500, "status": "gold"},
        {"user_id": 2, "type": "credit", "account_number": "ID--b2-w-231245-g9", "bank_id": 2, "currency": "EUR", "amount": 600, "status": "silver"},
        {"user_id": 1, "type": "credit", "account_number": "ID--a3-b-221645-c9", "bank_id": 1, "currency": "USD", "amount": 300, "status": "platinum"},
        {"user_id": 2, "type": "debit", "account_number": "ID--u3-w-211645-o8", "bank_id": 2, "currency": "EUR", "amount": 0, "status": "gold"},
        {"user_id": 2, "type": "debit", "account_number": "ID--d4-123-v9-7778", "bank_id": 0, "currency": "UAH", "amount": "n", "status": "gold"},
    ]
    print(add_accounts(*account_dicts))

    print("\n=== TRANSFERS ===")
    print(transfer_money(1, 2, 200, "USD"))  
    print(transfer_money(3, 4, 100, "USD"))   
    print(transfer_money(2, 3, 50, "EUR"))    


    print("\n=== USER TRANSACTIONS (user_id=1) FOR LAST 3 MONTHS ===")
    print(user_transactions_last_3_months(1))

    print("\n=== DELETE INCOMPLETE USERS/ACCOUNTS ===")
    print(delete_incomplete_users_and_accounts())

    print("\n=== BANK WITH MOST ACTIVE USERS ===")
    print(bank_with_most_active_users())

    print("\n=== BANK WITH OLDEST CLIENT ===")
    print(bank_with_oldest_client())

    print("\n=== BANK WITH BIGGEST CAPITAL ===")
    print(bank_with_biggest_capital())

    print("\n=== USERS WITH DEBT ===")
    print(get_users_with_debt())

    print("\n=== ASSIGN RANDOM DISCOUNTS ===")
    print(assign_random_discounts())

if __name__ == "__main__":
    main()
