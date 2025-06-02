import argparse
import sqlite3

def main():
    parser = argparse.ArgumentParser(
        description="Initial DB setup: creates a database structure SQLite"
    )
    parser.add_argument(
        '--db',
        default='database.db',
        help='Name of SQLite file'
    )
    parser.add_argument(
        '--unique-user-names',
        action='store_true',
        help='enable UNIQUE for fields User(Name, Surname)'
    )
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.execute('PRAGMA foreign_keys = ON;')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Bank (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS "Transaction" (
        id INTEGER PRIMARY KEY,
        bank_sender_name TEXT NOT NULL,
        account_sender_id INTEGER NOT NULL,
        bank_receiver_name TEXT NOT NULL,
        account_receiver_id INTEGER NOT NULL,
        sent_currency TEXT NOT NULL,
        sent_amount REAL NOT NULL,
        datetime TEXT
    );
    ''')

    unique_constraint = ",\n        UNIQUE(name, surname)" if args.unique_user_names else ""

    user_sql = f"""
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        birth_day TEXT,
        accounts TEXT NOT NULL
        {unique_constraint}
    );
    """
    cur.execute(user_sql)

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Account (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        account_number TEXT NOT NULL UNIQUE,
        bank_id INTEGER NOT NULL,
        currency TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES User(id),
        FOREIGN KEY(bank_id) REFERENCES Bank(id)
    );
    ''')

    conn.commit()
    conn.close()
    print(f"Database '{args.db}' initialized successfully.")


if __name__ == '__main__':
    main()
