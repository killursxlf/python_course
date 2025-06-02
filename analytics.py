import random
from db import with_db_connection
from helpers import api_response
from queries import (
    QUERY_ALL_USER_IDS,
    QUERY_USERS_WITH_DEBT,
    QUERY_BANK_WITH_BIGGEST_CAPITAL,
    QUERY_BANK_WITH_OLDEST_CLIENT,
    QUERY_BANK_MOST_ACTIVE_USERS,
    QUERY_DELETE_INCOMPLETE_ACCOUNTS,
    QUERY_DELETE_INCOMPLETE_USERS,
    QUERY_USER_ACCOUNTS,
    QUERY_USER_TRANSACTIONS_LAST_3M,
)


def safe_db_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return {"success": False, "message": str(e), "status_code": 500}


@with_db_connection
def assign_random_discounts(cur):
    def _core():
        cur.execute(QUERY_ALL_USER_IDS)
        all_user_ids = [row[0] for row in cur.fetchall()]
        num_users = min(len(all_user_ids), random.randint(1, 10))
        chosen_users = random.sample(all_user_ids, num_users)
        discounts = {uid: random.choice([25, 30, 50]) for uid in chosen_users}
        return {"success": True, "message": "Discounts assigned", "status_code": 200, "discounts": discounts}

    result = safe_db_call(_core, "assign_random_discounts")
    return api_response(**result)


@with_db_connection
def get_users_with_debt(cur):
    def _core():
        cur.execute(QUERY_USERS_WITH_DEBT)
        users = [f"{first} {last}" for first, last in cur.fetchall()]
        return {"success": True, "message": "Users with debts", "status_code": 200, "users": users}

    result = safe_db_call(_core, "get_users_with_debt")
    return api_response(**result)


@with_db_connection
def bank_with_biggest_capital(cur):
    def _core():
        cur.execute(QUERY_BANK_WITH_BIGGEST_CAPITAL)
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "No data", "status_code": 404}
        bank_id, name, total = row
        return {"success": True, "bank_id": bank_id, "name": name, "capital": total, "status_code": 200}

    result = safe_db_call(_core, "bank_with_biggest_capital")
    return api_response(**result)


@with_db_connection
def bank_with_oldest_client(cur):
    def _core():
        cur.execute(QUERY_BANK_WITH_OLDEST_CLIENT)
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "No data", "status_code": 404}
        bank_id, bank_name, user_id, user_name, user_surname, birth_day = row
        client_full = f"{user_name} {user_surname}"
        return {
            "success": True,
            "bank_id": bank_id,
            "bank_name": bank_name,
            "user_id": user_id,
            "client": client_full,
            "birth_day": birth_day,
            "status_code": 200
        }

    result = safe_db_call(_core, "bank_with_oldest_client")
    return api_response(**result)


@with_db_connection
def bank_with_most_active_users(cur):
    def _core():
        cur.execute(QUERY_BANK_MOST_ACTIVE_USERS)
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "No data", "status_code": 404}
        bank_name, user_count = row
        return {"success": True, "bank_name": bank_name, "user_count": user_count, "status_code": 200}

    result = safe_db_call(_core, "bank_with_most_active_users")
    return api_response(**result)


@with_db_connection
def delete_incomplete_users_and_accounts(cur):
    def _core():
        cur.execute(QUERY_DELETE_INCOMPLETE_ACCOUNTS)
        accounts_deleted = cur.rowcount
        cur.execute(QUERY_DELETE_INCOMPLETE_USERS)
        users_deleted = cur.rowcount
        return {"success": True, "accounts_deleted": accounts_deleted, "users_deleted": users_deleted, "status_code": 200}

    result = safe_db_call(_core, "delete_incomplete_users_and_accounts")
    return api_response(**result)


@with_db_connection
def user_transactions_last_3_months(cur, user_id):
    def _core():
        cur.execute(QUERY_USER_ACCOUNTS, (user_id,))
        account_ids = [row[0] for row in cur.fetchall()]
        if not account_ids:
            return {"success": False, "status_code": 404}

        placeholders = ",".join("?" for _ in account_ids)
        cur.execute(QUERY_USER_TRANSACTIONS_LAST_3M(placeholders), account_ids)
        transactions = cur.fetchall()
        return {"success": True, "transactions": transactions, "status_code": 200}

    result = safe_db_call(_core, "user_transactions_last_3_months")
    return api_response(**result)
