# ATM_INTERFACE
The ATM Simulator is a Python-based console application that emulates the basic functionalities of an Automated Teller Machine (ATM). It allows users to perform common banking operations such as:

Authenticate using a PIN.
Check balance to view the current account balance.
Deposit money to add funds.
Withdraw money with balance validation.
Change PIN for security purposes.
View mini statement, displaying the last 5 transactions.
Exit the ATM when finished.

## 🔥 Key Features:
Authentication System:

Users are required to enter a 4-digit PIN to access the ATM.
The program allows only 3 incorrect PIN attempts before locking the system.
Transaction Management:

Users can deposit or withdraw money.
The balance is updated in real-time.
A mini statement displays the last 5 transactions.
PIN Security:

Users can change their PIN securely by providing the current PIN.
Validates the format of the new PIN (4 digits only).
Error Handling:

Proper input validation ensures that invalid values (non-numeric or negative) are handled gracefully.
Includes warnings for incorrect PIN attempts.

### 🛠️ Technologies Used:
Programming Language: Python
Concepts Applied:
Object-Oriented Programming (OOP)
Exception Handling
List operations (for mini statement)
User input validation
Looping and conditionals

#### 🌟 How It Works:
Start: The program launches with a welcome message and asks for PIN authentication.
Menu Options:
After successful authentication, users can select options from the menu.
Transactions:
Deposits and withdrawals are recorded in the mini statement.
The balance is displayed after each transaction.
Security:
After 3 incorrect PIN attempts, the ATM locks.
Exit: The user can exit the program at any time by selecting the Exit option.
