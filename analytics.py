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


@with_db_connection
def assign_random_discounts(conn):
    """
    Randomly choose up to 10 users and assign them a random discount (25, 30, or 50).
    Returns:
        dict: {"success": bool, "message": str, "status_code": int, "discounts": dict}
    """
    try:
        cur = conn.cursor()
        cur.execute(QUERY_ALL_USER_IDS)
        all_user_ids = [row[0] for row in cur.fetchall()]
        num_users = min(len(all_user_ids), random.randint(1, 10))
        chosen_users = random.sample(all_user_ids, num_users)
        discounts = {uid: random.choice([25, 30, 50]) for uid in chosen_users}
        return api_response(True, "Discounts assigned", 200, "info") | {"discounts": discounts}
    except Exception as e:
        return api_response(False, str(e), 500, "error")


@with_db_connection
def get_users_with_debt(conn):
    """
    Get full names of users who have debts (negative balance on any account).
    Returns:
        dict: {"success": bool, "message": str, "status_code": int, "users": list[str]}
    """
    try:
        cur = conn.cursor()
        cur.execute(QUERY_USERS_WITH_DEBT)
        users = ["{} {}".format(name, surname) for name, surname in cur.fetchall()]
        return api_response(True, "Users with debts", 200, "info") | {"users": users}
    except Exception as e:
        return api_response(False, str(e), 500, "error")


@with_db_connection
def bank_with_biggest_capital(conn):
    """
    Find the bank with the largest capital (sum of all its accounts' amounts).
    Returns:
        dict: {"success": bool, "message": str, "status_code": int, "bank_id": int, "name": str, "capital": float}
    """
    try:
        cur = conn.cursor()
        cur.execute(QUERY_BANK_WITH_BIGGEST_CAPITAL)
        row = cur.fetchone()
        if not row:
            return api_response(False, "No data", 404, "warning")
        bank_id, name, total = row
        return api_response(True, f"Bank: {name}", 200, "info") | {"bank_id": bank_id, "name": name, "capital": total}
    except Exception as e:
        return api_response(False, str(e), 500, "error")


@with_db_connection
def bank_with_oldest_client(conn):
    """
    Find the bank that serves the oldest client (minimum birth_day).
    Returns:
        dict: {"success": bool, "message": str, "status_code": int,
               "bank_id": int, "bank_name": str, "user_id": int, "client": str, "birth_day": str}
    """
    try:
        cur = conn.cursor()
        cur.execute(QUERY_BANK_WITH_OLDEST_CLIENT)
        row = cur.fetchone()
        if not row:
            return api_response(False, "No data", 404, "warning")
        bank_id, bank_name, user_id, user_name, user_surname, birth_day = row
        return api_response(True, "Found", 200, "info") | {
            "bank_id": bank_id,
            "bank_name": bank_name,
            "user_id": user_id,
            "client": f"{user_name} {user_surname}",
            "birth_day": birth_day
        }
    except Exception as e:
        return api_response(False, str(e), 500, "error")


@with_db_connection
def bank_with_most_active_users(conn):
    """
    Find the bank with the highest number of unique users who performed outbound transactions.
    Returns:
        dict: {"success": bool, "message": str, "status_code": int, "bank_name": str, "user_count": int}
    """
    try:
        cur = conn.cursor()
        cur.execute(QUERY_BANK_MOST_ACTIVE_USERS)
        row = cur.fetchone()
        if not row:
            return api_response(False, "No data", 404, "warning")
        bank_name, user_count = row
        return api_response(True, "Found", 200, "info") | {"bank_name": bank_name, "user_count": user_count}
    except Exception as e:
        return api_response(False, str(e), 500, "error")


@with_db_connection
def delete_incomplete_users_and_accounts(conn):
    """
    Delete users and accounts that do not have complete information.
    Returns:
        dict: {"success": bool, "message": str, "status_code": int, "accounts_deleted": int, "users_deleted": int}
    """
    try:
        cur = conn.cursor()
        cur.execute(QUERY_DELETE_INCOMPLETE_ACCOUNTS)
        accounts_deleted = cur.rowcount
        cur.execute(QUERY_DELETE_INCOMPLETE_USERS)
        users_deleted = cur.rowcount
        return api_response(True, "Deleted incomplete data", 200, "info") | {
            "accounts_deleted": accounts_deleted, "users_deleted": users_deleted}
    except Exception as e:
        return api_response(False, str(e), 500, "error")


@with_db_connection
def user_transactions_last_3_months(conn, user_id):
    """
    Get all transactions of a particular user for the past 3 months.
    Returns:
        dict: {"success": bool, "message": str, "status_code": int, "transactions": list[tuple]}
    """
    try:
        cur = conn.cursor()
        cur.execute(QUERY_USER_ACCOUNTS, (user_id,))
        account_ids = [row[0] for row in cur.fetchall()]
        if not account_ids:
            return api_response(False, "No accounts for user", 404, "warning")
        placeholders = ",".join("?" for _ in account_ids)
        cur.execute(QUERY_USER_TRANSACTIONS_LAST_3M(placeholders), account_ids)
        transactions = cur.fetchall()
        return api_response(True, "Found transactions", 200, "info") | {"transactions": transactions}
    except Exception as e:
        return api_response(False, str(e), 500, "error")
