import requests
import csv
import os
from utils import check_db_connection, create_db_connection, close_db_connection
from constants import CURRENCY_API_URL
from dotenv import load_dotenv

load_dotenv()

CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")

def parse_user_name(user):
    full_name = user.get("user_full_name", "")
    parts = full_name.split(maxsplit=1)
    name = parts[0] if parts else ""
    surname = parts[1] if len(parts) > 1 else ""
    user["name"] = name
    user["surname"] = surname
    return user

@check_db_connection
def add_user(conn, *users):
    if len(users) == 1 and isinstance(users[0], list):
        users = users[0]
    results = []
    for user in users:
        try:
            full_name = user.get("full_name")
            name, surname = full_name.split(" ")
            birth_day = user.get("birth_day")
            accounts = user.get("accounts")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)",
                (name, surname, birth_day, accounts)
            )
            results.append({"status": "success", "user": user})
        except Exception as e:
            results.append({"status": "error", "user": user, "error": str(e)})
    return results

@check_db_connection
def add_bank(conn, *banks):
    if len(banks) == 1 and isinstance(banks[0], list):
        banks = banks[0]
    results = []
    for bank in banks:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO Bank (name) VALUES (?)",
                (bank.get("name"),)
            )
            results.append({"id": cur.lastrowid, "bank": bank})
        except Exception as e:
            return {"success": False, "message": f"Ошибка добавления банка: {e}"}
    conn.commit()
    return {"success": True, "message": "Банк(и) успешно добавлен(ы)", "data": results}


@check_db_connection
def add_account(conn, *accounts):
    if len(accounts) == 1 and isinstance(accounts[0], list):
        accounts = accounts[0]
    results = []
    for account in accounts:
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO Account 
                (user_id, type, account_number, bank_id, currency, amount, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    account.get("user_id"),
                    account.get("type"),
                    account.get("account_number"),
                    account.get("bank_id"),
                    account.get("currency"),
                    account.get("amount"),
                    account.get("status"),
                )
            )
            results.append({"id": cur.lastrowid, "account": account})
        except Exception as e:
            return {"success": False, "message": f"Ошибка добавления счёта: {e}"}
    conn.commit()
    return {"success": True, "message": "Счёт(а) успешно добавлен(ы)", "data": results}

def _read_csv(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def _parse_users_csv(rows):
    return [parse_user_name(row) for row in rows]

@check_db_connection
def add_users_from_csv(conn, path):
    try:
        users = _parse_users_csv(_read_csv(path))
        return add_user(users)
    except Exception as e:
        return {"success": False, "message": f"Ошибка импорта пользователей: {e}"}

@check_db_connection
def add_banks_from_csv(conn, path):
    try:
        banks = _read_csv(path)
        return add_bank(banks)
    except Exception as e:
        return {"success": False, "message": f"Ошибка импорта банков: {e}"}

@check_db_connection
def add_accounts_from_csv(conn, path):
    try:
        accounts = _read_csv(path)
        return add_account(accounts)
    except Exception as e:
        return {"success": False, "message": f"Ошибка импорта счетов: {e}"}

@check_db_connection
def update_user(conn, user_id, **fields):
    try:
        if "user_full_name" in fields:
            fields = parse_user_name(fields)
        columns = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values())
        values.append(user_id)
        cur = conn.cursor()
        cur.execute(f"UPDATE User SET {columns} WHERE id=?", values)
        conn.commit()
        if cur.rowcount == 0:
            return {"success": False, "message": "Пользователь не найден"}
        return {"success": True, "message": "Пользователь обновлён"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка обновления пользователя: {e}"}

@check_db_connection
def update_bank(conn, bank_id, **fields):
    try:
        columns = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values())
        values.append(bank_id)
        cur = conn.cursor()
        cur.execute(f"UPDATE Bank SET {columns} WHERE id=?", values)
        conn.commit()
        if cur.rowcount == 0:
            return {"success": False, "message": "Банк не найден"}
        return {"success": True, "message": "Банк обновлён"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка обновления банка: {e}"}

@check_db_connection
def update_account(conn, account_id, **fields):
    try:
        columns = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values())
        values.append(account_id)
        cur = conn.cursor()
        cur.execute(f"UPDATE Account SET {columns} WHERE id=?", values)
        conn.commit()
        if cur.rowcount == 0:
            return {"success": False, "message": "Счёт не найден"}
        return {"success": True, "message": "Счёт обновлён"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка обновления счёта: {e}"}

@check_db_connection
def delete_user(conn, user_id):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM User WHERE id=?", (user_id,))
        conn.commit()
        if cur.rowcount == 0:
            return {"success": False, "message": "Пользователь не найден"}
        return {"success": True, "message": "Пользователь удалён"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка удаления пользователя: {e}"}

@check_db_connection
def delete_bank(conn, bank_id):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Bank WHERE id=?", (bank_id,))
        conn.commit()
        if cur.rowcount == 0:
            return {"success": False, "message": "Банк не найден"}
        return {"success": True, "message": "Банк удалён"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка удаления банка: {e}"}

@check_db_connection
def delete_account(conn, account_id):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Account WHERE id=?", (account_id,))
        conn.commit()
        if cur.rowcount == 0:
            return {"success": False, "message": "Счёт не найден"}
        return {"success": True, "message": "Счёт удалён"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка удаления счёта: {e}"}

def get_exchange_rate(from_currency, to_currency):
    if from_currency == to_currency:
        return 1.0
    params = {
        "apikey": CURRENCY_API_KEY,
        "base_currency": from_currency,
        "currencies": to_currency
    }
    try:
        response = requests.get(CURRENCY_API_URL, params=params, timeout=5)
        if response.status_code == 429:
            raise Exception("Превышен лимит запросов к валютному API")
        data = response.json()
        return data["data"][to_currency]
    except Exception as e:
        raise Exception(f"Ошибка получения курса валют: {e}")

@check_db_connection
def transfer_money(conn, sender_account_id, receiver_account_id, amount):
    try:
        cur = conn.cursor()
        # Получаем данные отправителя
        cur.execute("SELECT amount, currency FROM Account WHERE id=?", (sender_account_id,))
        sender = cur.fetchone()
        if not sender:
            return {"success": False, "message": "Счёт отправителя не найден"}
        sender_balance, sender_currency = sender
        if sender_balance < amount:
            return {"success": False, "message": "Недостаточно средств на счёте отправителя"}

        # Получаем данные получателя
        cur.execute("SELECT currency FROM Account WHERE id=?", (receiver_account_id,))
        receiver = cur.fetchone()
        if not receiver:
            return {"success": False, "message": "Счёт получателя не найден"}
        receiver_currency = receiver[0]

        # Конвертация валюты, если нужно
        if sender_currency != receiver_currency:
            rate = get_exchange_rate(sender_currency, receiver_currency)
            converted_amount = amount * rate
        else:
            converted_amount = amount

        # Обновляем балансы
        cur.execute("UPDATE Account SET amount = amount - ? WHERE id=?", (amount, sender_account_id))
        cur.execute("UPDATE Account SET amount = amount + ? WHERE id=?", (converted_amount, receiver_account_id))

        # Добавляем запись о транзакции
        cur.execute("""
            INSERT INTO "Transaction" (
                bank_sender_name, account_sender_id, bank_receiver_name, account_receiver_id,
                sent_currency, sent_amount, datetime
            ) VALUES (
                (SELECT name FROM Bank WHERE id=(SELECT bank_id FROM Account WHERE id=?)),
                ?, 
                (SELECT name FROM Bank WHERE id=(SELECT bank_id FROM Account WHERE id=?)),
                ?, ?, ?, datetime('now')
            )
        """, (
            sender_account_id, sender_account_id,
            receiver_account_id, receiver_account_id,
            sender_currency, amount
        ))
        conn.commit()
        return {"success": True, "message": "Перевод выполнен успешно"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка перевода: {e}"}