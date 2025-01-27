-- Act as expert software, Engineering expert in functional design patterns.
-- The problem has Entities, Operations, and Conditions invariants that have to be always.
-- The Entities will be model with ADT types.
-- The Operations will be model as functions.
-- But how do we model the conditions/invariance ??
-- Nice lets proceed to model a snack machine in this functional rich domain principles. Here is the Haskell code
-- Translate the code into python and using rich functional patterns, avoid as much as posable oop

import Data.List (find)

-- 1. Define the types (Entities)
data Snack
  = Doritos
  | Oreos
  | Pringles
  | ReesePeanutButterCups
  | Goldfish
  | Cheetos
  | MMs
  | CheezIts
  | GummyBears
  | Fritos
  deriving (Show, Eq)

data Stock = Stock
  { snack :: Snack,
    price :: Float, -- positive float
    amount :: Int -- positive integer
  }
  deriving (Show, Eq)

data Machine = Machine {stocks :: [Stock]} deriving (Show, Eq)

data Account = Account
  { name :: String,
    balance :: Float, -- positive float
    snacks :: [Snack] -- list of snacks purchased
  }
  deriving (Show, Eq)

-- 2. Define error types for validations
data ValuePositiveError = ValuePositiveError deriving (Show, Eq)

data PurchaseError = InsufficientFunds | InsufficientStock deriving (Show, Eq)

-- 3. Define helper functions to ensure positive values
positiveFloat :: Float -> Either ValuePositiveError Float
positiveFloat value
  | value > 0 = Right value
  | otherwise = Left ValuePositiveError

positiveInt :: Int -> Either ValuePositiveError Int
positiveInt value
  | value > 0 = Right value
  | otherwise = Left ValuePositiveError

-- 4. Define the functions to create new entities, with validation
newStock :: Snack -> Float -> Int -> Either ValuePositiveError Stock
newStock snack price amount = do
  validPrice <- positiveFloat price
  validAmount <- positiveInt amount
  return $ Stock snack validPrice validAmount

newMachine :: [Stock] -> Machine
newMachine stocks = Machine stocks

newAccount :: String -> Float -> Either ValuePositiveError Account
newAccount name balance = do
  validBalance <- positiveFloat balance
  return $ Account name validBalance []

-- 5. Define functions to interact with entities
getBalance :: Account -> Float
getBalance = balance

getStock :: Machine -> [Stock]
getStock = stocks

getBoughtProducts :: Account -> [Snack]
getBoughtProducts = snacks

-- 6. Define the Buy function, which validates balance and stock
buy :: Account -> Snack -> Machine -> Either PurchaseError (Account, Machine)
buy account snack machine = do
  -- Find the stock for the given snack
  let stock = findStock snack (stocks machine)
  case stock of
    Nothing -> Left InsufficientStock
    Just s -> do
      -- Check if the account has enough balance
      if balance account >= price s
        then do
          -- Check if there is sufficient stock
          if amount s > 0
            then do
              let newAccount = account {balance = balance account - price s, snacks = snack : snacks account}
              let newStock = s {amount = amount s - 1}
              let newMachine = machine {stocks = replaceStock snack newStock (stocks machine)}
              Right (newAccount, newMachine)
            else Left InsufficientStock
        else Left InsufficientFunds

-- Find the stock for the given snack
findStock :: Snack -> [Stock] -> Maybe Stock
findStock snack = find (\s -> snack == snack s) -- Accessing 'snack' field of Stock

-- Replace stock in the machine
replaceStock :: Snack -> Stock -> [Stock] -> [Stock]
replaceStock _ _ [] = []
replaceStock snack newStock (x : xs)
  | snack == snack x = newStock : xs -- Accessing 'snack' field of Stock
  | otherwise = x : replaceStock snack newStock xs
