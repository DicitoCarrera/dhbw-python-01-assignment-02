import sqlite3
from typing import List, Optional

from domain.VendingMachine import Account, Machine, Snack, Stock

# === 7. Persistence Layer (SQLite) ===

DB_NAME = "vending_machine.db"


def get_connection():
    # Increase the timeout to allow SQLite to wait for a lock to be released
    return sqlite3.connect(database=DB_NAME, timeout=10)  # Timeout in seconds


# Initialize the database tables if they don't exist
def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Create necessary tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                balance REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snack TEXT,
                price REAL,
                amount INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS machines (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS machine_stocks (
                machine_id INTEGER,
                stock_id INTEGER,
                FOREIGN KEY (machine_id) REFERENCES machines(id),
                FOREIGN KEY (stock_id) REFERENCES stocks(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchased_snacks (
                account_name TEXT,
                snack_name TEXT,
                FOREIGN KEY (account_name) REFERENCES accounts(name),
                FOREIGN KEY (snack_name) REFERENCES snacks(name)
            )
        """)

        conn.commit()


# Add new account to the database
def save_account(account: Account):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO accounts (name, balance) VALUES (?, ?)",
            (account.name, account.balance),
        )
        conn.commit()


# Add new stock to the database
def save_stock(stock: Stock):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stocks (snack, price, amount) VALUES (?, ?, ?)",
            (stock.snack.name, stock.price, stock.amount),
        )
        conn.commit()


# Add new machine to the database
def save_machine(machine: Machine):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO machines DEFAULT VALUES")
        machine_id = cursor.lastrowid

        # Insert all stocks in a single transaction
        for stock in machine.stocks:
            cursor.execute(
                "INSERT INTO stocks (snack, price, amount) VALUES (?, ?, ?)",
                (stock.snack.name, stock.price, stock.amount),
            )
            stock_id = cursor.lastrowid  # Get the ID of the newly inserted stock
            cursor.execute(
                "INSERT INTO machine_stocks (machine_id, stock_id) VALUES (?, ?)",
                (machine_id, stock_id),
            )

        conn.commit()


# Retrieve an Account by name
def get_account_by_name(name: str) -> Optional[Account]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return Account(name=row[1], balance=row[2], snacks=[])
        return None


# Retrieve all Stocks for a specific Machine
def get_machine_stocks(machine_id: int) -> List[Stock]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT s.snack, s.price, s.amount
            FROM stocks s
            JOIN machine_stocks ms ON s.id = ms.stock_id
            WHERE ms.machine_id = ?
        """,
            (machine_id,),
        )
        rows = cursor.fetchall()
        return [Stock(snack=Snack[s[0]], price=s[1], amount=s[2]) for s in rows]


# Get the stock ID by snack name
def get_stock_id_by_snack(snack: Snack) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM stocks WHERE snack = ?", (snack.name,))
        row = cursor.fetchone()
        return row[0] if row else -1


# Update account balance after a purchase
def update_account_balance(account_name: str, new_balance: float):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE accounts SET balance = ? WHERE name = ?",
            (new_balance, account_name),
        )
        conn.commit()


# Update stock amount after a purchase
def update_machine_stock(snack: Snack, new_amount: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE stocks SET amount = ? WHERE snack = ?", (new_amount, snack.name)
        )
        conn.commit()


# Save purchased snacks in the account
def save_purchased_snacks(account_name: str, snacks: List[Snack]):
    with get_connection() as conn:
        cursor = conn.cursor()

        # First, delete any previous snacks from the account
        cursor.execute(
            "DELETE FROM purchased_snacks WHERE account_name = ?", (account_name,)
        )

        # Insert the new snacks into the purchased_snacks table
        for snack in snacks:
            cursor.execute(
                "INSERT INTO purchased_snacks (account_name, snack_name) VALUES (?, ?)",
                (account_name, snack.name),
            )

        conn.commit()
