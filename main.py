from ast import List


def main():
    print("Hello from assignment-02!")


if __name__ == "__main__":
    main()

type Snack:
Doritos
Oreos
Pringles
Reese’s Peanut Butter Cups
Goldfish
Cheetos
M&Ms
Cheez-Its
Gummy Bears
Fritos

type Stock:
    snack: Snack
    price: float > 0
    amount: int > 0

type Machine:
    list(Stock)

type Account:
    name: str
    balance: float > 0
    snack: List(Snacks)

fn newStock (Snack, float, int) -> Either Stock , ValuePositiveError:

fn newMachine (List(Stock)) -> Machine

fn newAccount (str, float ) -> Either Account, ValuePositiveError

fn GetBalance: Account -> Balance:
 return Account.balance

fn Deposit: Account, Balance, -> Account :
 -- Balance > 0:

fn GetStock: Machine -> List(Stock)

fn Buy: Account, Snakcs, Machine -> Left Account, Machine; Rigth InsuccinetFunds, InsuficcinetStock...:
 -- Balance > 0:
 -- Machine (snack) > 0:

fn GetBoughtPRoducts: Account -> List(Snack)
 return Account.snack

fn GetBoughtPRoductsConsole = GetBoughtPRoducts => print # Console

fn GetBoughtPRoductsHTML = GetBoughtPRoducts => HTML # Website
