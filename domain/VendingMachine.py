from dataclasses import dataclass
from enum import Enum, auto
from typing import List

# === 1. Define the types (Entities) ===


class Snack(Enum):
    DORITOS = auto()
    OREOS = auto()
    PRINGLES = auto()
    REESE_PEANUT_BUTTER_CUPS = auto()
    GOLDFISH = auto()
    CHEETOS = auto()
    MMS = auto()
    CHEEZ_ITS = auto()
    GUMMY_BEARS = auto()
    FRITOS = auto()

    def __repr__(self):
        return f"Snack({self.name})"


@dataclass
class Stock:
    snack: Snack
    price: float
    amount: int


@dataclass
class Machine:
    stocks: List[Stock]


@dataclass
class Account:
    name: str
    balance: float
    snacks: List[Snack]


# === 2. Define error types for validations ===


class ValuePositiveError(Exception):
    pass


class PurchaseError(Exception):
    pass


class InsufficientFunds(PurchaseError):
    pass


class InsufficientStock(PurchaseError):
    pass


# === 3. Define helper functions to ensure positive values ===


def positive_float(value: float) -> ValuePositiveError | float:
    if value > 0:
        return value
    return ValuePositiveError("Value must be positive")


def positive_int(value: int) -> ValuePositiveError | int:
    if value > 0:
        return value
    return ValuePositiveError("Value must be positive")


# === 4. Define the functions to create new entities, with validation ===


def new_stock(snack: Snack, price: float, amount: int) -> ValuePositiveError | Stock:
    valid_price: ValuePositiveError | float = positive_float(value=price)
    if isinstance(valid_price, ValuePositiveError):
        return valid_price

    valid_amount: ValuePositiveError | int = positive_int(value=amount)
    if isinstance(valid_amount, ValuePositiveError):
        return valid_amount

    return Stock(snack=snack, price=valid_price, amount=valid_amount)


def new_machine(stocks: List[Stock]) -> Machine:
    return Machine(stocks=stocks)


def new_account(name: str, balance: float) -> ValuePositiveError | Account:
    valid_balance: ValuePositiveError | float = positive_float(value=balance)

    if isinstance(valid_balance, ValuePositiveError):
        return valid_balance

    return Account(name=name, balance=valid_balance, snacks=[])


# === 5. Define functions to interact with entities ===


def get_balance(account: Account) -> float:
    return account.balance


def get_stocks(machine: Machine) -> List[Stock]:
    return machine.stocks


def get_bought_products(account: Account) -> List[Snack]:
    return account.snacks


# === 6. Define the Buy function, which validates balance and stock ===


def buy(
    account: Account, snack: Snack, machine: Machine
) -> PurchaseError | tuple[Account, Machine]:
    stock: Stock | None = find_stock(snack=snack, stocks=machine.stocks)

    if stock is None:
        return InsufficientStock()

    if account.balance < stock.price:
        return InsufficientStock()

    if stock.amount == 0:
        return InsufficientStock()

    new_account = Account(
        name=account.name,
        balance=account.balance - stock.price,
        snacks=[snack] + account.snacks,  # Add the snack to the account's snack list
    )
    new_stock = Stock(snack=snack, price=stock.price, amount=stock.amount - 1)
    new_machine = Machine(
        stocks=replace_stock(snack=snack, new_stock=new_stock, stocks=machine.stocks)
    )

    return new_account, new_machine


# === Helper functions ===


def find_stock(snack: Snack, stocks: List[Stock]) -> Stock | None:
    for s in stocks:
        if s.snack == snack:
            return s
    return None


def replace_stock(snack: Snack, new_stock: Stock, stocks: List[Stock]) -> List[Stock]:
    return [new_stock if s.snack == snack else s for s in stocks]
