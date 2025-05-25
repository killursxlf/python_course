from db import with_db_connection
from models import User, Bank, Account
from logging_config import get_logger
from helpers import api_response     
from transfer import do_transfer

logger = get_logger(__name__)

def unpack_rows(*args):
    if len(args) == 1 and isinstance(args[0], list):
        return args[0]
    return list(args)


def insert_rows(conn, table, fields, objs):
    cur = conn.cursor()
    placeholders = ', '.join(['?'] * len(fields))
    sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
    for obj in objs:
        cur.execute(sql, [getattr(obj, f) for f in fields])
    return len(objs)


def update_row(conn, table, fields, pk_field, obj):
    cur = conn.cursor()
    set_clause = ', '.join([f"{f}=?" for f in fields])
    sql = f"UPDATE {table} SET {set_clause} WHERE {pk_field}=?"
    params = [getattr(obj, f) for f in fields] + [getattr(obj, pk_field)]
    cur.execute(sql, params)
    return cur.rowcount


def delete_row(conn, table, pk_field, pk_value):
    cur = conn.cursor()
    sql = f"DELETE FROM {table} WHERE {pk_field}=?"
    cur.execute(sql, (pk_value,))
    return cur.rowcount


@with_db_connection
def add_users(conn, *users):
    rows = unpack_rows(*users)
    fields = ["name", "surname", "birth_day", "accounts"]
    try:
        count = insert_rows(conn, "User", fields, rows)
        return api_response(True, f"Users added: {count}")
    except Exception as e:
        return api_response(False, f"Error adding user: {e}", 500, "error")


@with_db_connection
def update_user(conn, user: User):
    fields = ["name", "surname", "birth_day", "accounts"]
    try:
        if user.id is None:
            return api_response(False, "User id is required for update", 400, "warning")
        rowcount = update_row(conn, "User", fields, "id", user)
        if rowcount == 0:
            return api_response(False, "User not found", 404, "warning")
        return api_response(True, f"User with id={user.id} updated")
    except Exception as e:
        return api_response(False, f"Error updating user: {e}", 500, "error")


@with_db_connection
def delete_user(conn, user_id: int):
    try:
        rowcount = delete_row(conn, "User", "id", user_id)
        if rowcount == 0:
            return api_response(False, "User not found", 404, "warning")
        return api_response(True, f"User with id={user_id} deleted")
    except Exception as e:
        return api_response(False, f"Error deleting user: {e}", 500, "error")


@with_db_connection
def add_banks(conn, *banks):
    rows = unpack_rows(*banks)
    fields = ["name"]
    try:
        count = insert_rows(conn, "Bank", fields, rows)
        return api_response(True, f"Banks added: {count}")
    except Exception as e:
        return api_response(False, f"Error adding bank: {e}", 500, "error")


@with_db_connection
def update_bank(conn, bank: Bank):
    fields = ["name"]
    try:
        if bank.id is None:
            return api_response(False, "Bank id is required for update", 400, "warning")
        rowcount = update_row(conn, "Bank", fields, "id", bank)
        if rowcount == 0:
            return api_response(False, "Bank not found", 404, "warning")
        return api_response(True, f"Bank with id={bank.id} updated")
    except Exception as e:
        return api_response(False, f"Error updating bank: {e}", 500, "error")


@with_db_connection
def delete_bank(conn, bank_id: int):
    try:
        rowcount = delete_row(conn, "Bank", "id", bank_id)
        if rowcount == 0:
            return api_response(False, "Bank not found", 404, "warning")
        return api_response(True, f"Bank with id={bank_id} deleted")
    except Exception as e:
        return api_response(False, f"Error deleting bank: {e}", 500, "error")


@with_db_connection
def add_accounts(conn, *accounts):
    rows = unpack_rows(*accounts)
    fields = ["user_id", "type", "account_number", "bank_id", "currency", "amount", "status"]
    try:
        count = insert_rows(conn, "Account", fields, rows)
        return api_response(True, f"Accounts added: {count}")
    except Exception as e:
        return api_response(False, f"Error adding account: {e}", 500, "error")


@with_db_connection
def update_account(conn, account: Account):
    fields = ["user_id", "type", "account_number", "bank_id", "currency", "amount", "status"]
    try:
        if account.id is None:
            return api_response(False, "Account id is required for update", 400, "warning")
        rowcount = update_row(conn, "Account", fields, "id", account)
        if rowcount == 0:
            return api_response(False, "Account not found", 404, "warning")
        return api_response(True, f"Account with id={account.id} updated")
    except Exception as e:
        return api_response(False, f"Error updating account: {e}", 500, "error")

@with_db_connection
def delete_account(conn, account_id: int):
    try:
        rowcount = delete_row(conn, "Account", "id", account_id)
        if rowcount == 0:
            return api_response(False, "Account not found", 404, "warning")
        return api_response(True, f"Account with id={account_id} deleted")
    except Exception as e:
        return api_response(False, f"Error deleting account: {e}", 500, "error")


@with_db_connection
def transfer_money(conn, sender_account_id: int, receiver_account_id: int, amount: float, currency: str):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, type, account_number, bank_id, currency, amount, status FROM Account WHERE id=?", (sender_account_id,))
        sender_row = cur.fetchone()
        if not sender_row:
            return api_response(False, "Sender account not found", 404, "warning")
        sender = Account(*sender_row)

        cur.execute("SELECT id, user_id, type, account_number, bank_id, currency, amount, status FROM Account WHERE id=?", (receiver_account_id,))
        receiver_row = cur.fetchone()
        if not receiver_row:
            return api_response(False, "Receiver account not found", 404, "warning")
        receiver = Account(*receiver_row)

        transfer_result = do_transfer(cur, sender, receiver, amount)
        if not transfer_result["success"]:
            return transfer_result

        cur.execute(
            '''INSERT INTO "Transaction"
               (bank_sender_name, account_sender_id, bank_receiver_name, account_receiver_id, sent_currency, sent_amount, datetime)
               VALUES (?, ?, ?, ?, ?, ?, datetime('now'))''',
            (
                _get_bank_name(cur, sender.bank_id),
                sender.id,
                _get_bank_name(cur, receiver.bank_id),
                receiver.id,
                sender.currency,
                amount
            )
        )
        return transfer_result

    except Exception as e:
        return api_response(False, f"Error during transfer: {e}", 500, "error")

def _get_bank_name(cur, bank_id):
    cur.execute("SELECT name FROM Bank WHERE id=?", (bank_id,))
    row = cur.fetchone()
    return row[0] if row else "Unknown"
