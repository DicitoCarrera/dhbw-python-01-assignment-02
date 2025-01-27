from dataclasses import dataclass
from enum import Enum, auto

# === 1. Define the types (Entities) ===


# Enum to model the Snack sum type
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
    stocks: list[Stock]


@dataclass
class Account:
    name: str
    balance: float
    snacks: list[Snack]


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


def new_machine(stocks: list[Stock]) -> Machine:
    return Machine(stocks=stocks)


def new_account(name: str, balance: float) -> ValuePositiveError | Account:
    valid_balance: ValuePositiveError | float = positive_float(value=balance)

    if isinstance(valid_balance, ValuePositiveError):
        return valid_balance

    return Account(name=name, balance=valid_balance, snacks=[])


# === 5. Define functions to interact with entities ===


def get_balance(account: Account) -> float:
    return account.balance


def get_stocks(machine: Machine) -> list[Stock]:
    return machine.stocks


def get_bought_products(account: Account) -> list[Snack]:
    return account.snacks


# === 6. Define the Buy function, which validates balance and stock ===


def buy(
    account: Account, snack: Snack, machine: Machine
) -> (
    PurchaseError
    | tuple[
        Account,
        Machine,
    ]
):
    stock: Stock | None = find_stock(snack=snack, stocks=machine.stocks)

    if stock is None:
        return InsufficientStock()

    if account.balance >= stock.price:
        if stock.amount > 0:
            new_account = Account(
                name=account.name,
                balance=account.balance - stock.price,
                snacks=[snack] + account.snacks,
            )
            new_stock = Stock(snack=snack, price=stock.price, amount=stock.amount - 1)
            new_machine = Machine(
                stocks=replace_stock(
                    snack=snack, new_stock=new_stock, stocks=machine.stocks
                )
            )
            return new_account, new_machine
        else:
            return InsufficientStock()
    else:
        return InsufficientFunds()


# === Helper functions ===


def find_stock(snack: Snack, stocks: list[Stock]) -> Stock | None:
    for s in stocks:
        if s.snack == snack:
            return s
    return None


def replace_stock(snack: Snack, new_stock: Stock, stocks: list[Stock]) -> list[Stock]:
    return [new_stock if s.snack == snack else s for s in stocks]


# === Example Usage ===

# Create snacks
doritos = Snack.DORITOS
oreos = Snack.OREOS

# Create stocks
stock1: ValuePositiveError | Stock = new_stock(snack=doritos, price=1.5, amount=10)
stock2: ValuePositiveError | Stock = new_stock(snack=oreos, price=2.0, amount=5)

# Create a machine
machine: Machine = new_machine(stocks=[stock1, stock2])

# Create an account
account: ValuePositiveError | Account = new_account(name="Alice", balance=20.0)

# Make a purchase
result = buy(account=account, snack=doritos, machine=machine)

match result:
    case PurchaseError():
        pass
    case (Account(), Machine()):
        account, machine = result

result = buy(account=account, snack=oreos, machine=machine)

print(result)

match result:
    case PurchaseError():
        pass
    case (Account(), Machine()):
        account, machine = result
