from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from domain.VendingMachine import (
    Account,
    Machine,
    PurchaseError,
    Snack,
    Stock,
    ValuePositiveError,
    buy,
    new_stock,
)
from persistence import (
    get_account_by_name,
    get_machine_stocks,
    initialize_db,
    save_account,
    save_machine,
    save_purchased_snacks,
    save_stock,
    update_account_balance,
    update_machine_stock,
)

# === 8. TUI with Rich ===

console = Console()


def display_account(account: Account):
    console.print(
        Panel(
            f"Account: {account.name}\nBalance: ${account.balance:.2f}",
            title="Account Info",
        )
    )
    if account.snacks:
        console.print("Purchased Snacks:", style="bold cyan")
        for snack in account.snacks:
            console.print(f"- {snack.name}")
    else:
        console.print("No snacks purchased yet.", style="dim")


def display_machine_stock(machine: Machine):
    table = Table(title="Machine Stock")
    table.add_column("Snack", justify="center")
    table.add_column("Price", justify="center")
    table.add_column("Amount", justify="center")

    for stock in machine.stocks:
        table.add_row(stock.snack.name, f"${stock.price:.2f}", str(stock.amount))

    console.print(table)


def buy_snack(account: Account, machine: Machine):
    snack_name = Prompt.ask("Enter snack name", choices=[snack.name for snack in Snack])
    snack = Snack[snack_name]

    result = buy(account=account, snack=snack, machine=machine)

    if isinstance(result, PurchaseError):
        console.print(f"[bold red]Purchase Error: {result}[/bold red]")
    else:
        new_account, new_machine = result

        # Save the changes in the database
        update_account_balance(
            account_name=account.name, new_balance=new_account.balance
        )
        update_machine_stock(snack=snack, new_amount=new_stock.amount)

        # Save the purchased snack in the account table in the database
        save_purchased_snacks(account_name=account.name, snacks=new_account.snacks)

        display_account(account=new_account)
        display_machine_stock(machine=new_machine)


def add_new_stock_to_machine(machine: Machine):
    snack_name = Prompt.ask("Enter snack name", choices=[snack.name for snack in Snack])

    snack = Snack[snack_name]

    price = float(
        Prompt.ask(
            prompt="Enter price",
            default="1.0",
        )
    )

    amount = int(
        Prompt.ask(
            prompt="Enter amount",
            default="5",
        )
    )

    result = new_stock(snack=snack, price=price, amount=amount)

    if isinstance(result, ValuePositiveError):
        console.print(f"[bold red]Error: {result}[/bold red]")
    else:
        machine.stocks.append(result)
        save_stock(result)  # Persist the new stock in the database
        console.print(f"[bold green]New snack added: {snack.name}[/bold green]")
        display_machine_stock(machine)


def show_main_menu(account: Account, machine: Machine):
    while True:
        console.clear()
        display_account(account=account)
        display_machine_stock(machine=machine)

        action = Prompt.ask(
            "Choose an action",
            choices=[
                "View Account",
                "View Machine Stock",
                "Buy Snack",
                "Add New Stock",
                "Exit",
            ],
        )

        if action == "View Account":
            display_account(account)
            console.input("Press Enter to return to main menu...")
        elif action == "View Machine Stock":
            display_machine_stock(machine)
            console.input("Press Enter to return to main menu...")
        elif action == "Buy Snack":
            buy_snack(account, machine)
            console.input("Press Enter to return to main menu...")
        elif action == "Add New Stock":
            add_new_stock_to_machine(machine)
            console.input("Press Enter to return to main menu...")
        elif action == "Exit":
            break


# Main entry point
def main():
    # Initialize DB and create tables if they don't exist
    initialize_db()

    # Simulate loading account and machine data
    account = get_account_by_name("Alice")

    if not account:
        account = Account(name="Alice", balance=20.0, snacks=[])
        save_account(account)

    machine_id = 1  # Assuming we have a single machine for now
    machine_stocks = get_machine_stocks(machine_id)

    # Initialize machine variable
    if not machine_stocks:
        stock1 = Stock(snack=Snack.DORITOS, price=1.5, amount=10)
        stock2 = Stock(snack=Snack.OREOS, price=2.0, amount=5)
        machine = Machine(stocks=[stock1, stock2])
        save_machine(machine)
    else:
        # If machine_stocks are found, load the existing machine with stocks
        machine = Machine(stocks=machine_stocks)

    # Now you can safely pass machine to show_main_menu
    show_main_menu(account=account, machine=machine)


if __name__ == "__main__":
    main()
