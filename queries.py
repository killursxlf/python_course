QUERY_ALL_USER_IDS = "SELECT id FROM User"

QUERY_USERS_WITH_DEBT = """
    SELECT DISTINCT u.name, u.surname
    FROM User u
    JOIN Account a ON a.user_id = u.id
    WHERE a.amount < 0
"""

QUERY_BANK_WITH_BIGGEST_CAPITAL = """
    SELECT b.id, b.name, SUM(a.amount) as total
    FROM Bank b
    JOIN Account a ON a.bank_id = b.id
    GROUP BY b.id
    ORDER BY total DESC
    LIMIT 1
"""

QUERY_BANK_WITH_OLDEST_CLIENT = """
    SELECT b.id, b.name, u.id, u.name, u.surname, u.birth_day
    FROM Bank b
    JOIN Account a ON a.bank_id = b.id
    JOIN User u ON a.user_id = u.id
    WHERE u.birth_day IS NOT NULL
    ORDER BY u.birth_day ASC
    LIMIT 1
"""

QUERY_BANK_MOST_ACTIVE_USERS = """
    SELECT t.bank_sender_name, COUNT(DISTINCT t.account_sender_id) as user_count
    FROM "Transaction" t
    GROUP BY t.bank_sender_name
    ORDER BY user_count DESC
    LIMIT 1
"""

QUERY_DELETE_INCOMPLETE_ACCOUNTS = """
    DELETE FROM Account
    WHERE account_number IS NULL OR account_number = ''
       OR currency IS NULL OR currency = ''
       OR status IS NULL OR status = ''
"""

QUERY_DELETE_INCOMPLETE_USERS = """
    DELETE FROM User
    WHERE name IS NULL OR name = ''
       OR surname IS NULL OR surname = ''
"""

QUERY_USER_ACCOUNTS = "SELECT id FROM Account WHERE user_id = ?"


UPDATE_ACCOUNT_AMOUNT_BY_ID = "UPDATE Account SET amount=? WHERE id=?"


SELECT_BANK_NAME_BY_ID = "SELECT name FROM Bank WHERE id=?"


INSERT_TRANSACTION = '''
    INSERT INTO "Transaction"
    (bank_sender_name, account_sender_id, bank_receiver_name, account_receiver_id, sent_currency, sent_amount, datetime)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
'''

SELECT_ACCOUNT_BY_ID = "SELECT id, user_id, type, account_number, bank_id, currency, amount, status FROM Account WHERE id=?"


def QUERY_USER_TRANSACTIONS_LAST_3M(placeholders):
    return f"""
        SELECT *
        FROM "Transaction"
        WHERE account_sender_id IN ({placeholders})
        AND datetime >= DATE('now', '-3 months')
        ORDER BY datetime DESC
    """


def insert_rows(conn, table, fields, objs):
    """
    Insert multiple rows into a table.
    :param conn: sqlite3.Connection
    :param table: str (table name)
    :param fields: list of column names
    :param objs: list of dataclass instances
    :return: int (number of inserted rows)
    """
    cur = conn.cursor()
    placeholders = ', '.join(['?'] * len(fields))
    sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
    for obj in objs:
        cur.execute(sql, [getattr(obj, f) for f in fields])
    return len(objs)


def update_row(conn, table, fields, pk_field, obj):
    """
    Update a single row in a table by primary key.
    :param conn: sqlite3.Connection
    :param table: str (table name)
    :param fields: list of column names to update
    :param pk_field: str (primary key field)
    :param obj: dataclass instance (must have pk_field as attribute)
    :return: int (number of affected rows)
    """
    cur = conn.cursor()
    set_clause = ', '.join([f"{f}=?" for f in fields])
    sql = f"UPDATE {table} SET {set_clause} WHERE {pk_field}=?"
    params = [getattr(obj, f) for f in fields] + [getattr(obj, pk_field)]
    cur.execute(sql, params)
    return cur.rowcount


def delete_row(conn, table, pk_field, pk_value):
    """
    Delete a row from a table by primary key.
    :param conn: sqlite3.Connection
    :param table: str (table name)
    :param pk_field: str (primary key field)
    :param pk_value: value of the primary key
    :return: int (number of affected rows)
    """
    cur = conn.cursor()
    sql = f"DELETE FROM {table} WHERE {pk_field}=?"
    cur.execute(sql, (pk_value,))
    return cur.rowcount
