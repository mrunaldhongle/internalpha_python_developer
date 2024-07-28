import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database setup
def setup_database():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT, 
                    balance REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    username TEXT, 
                    type TEXT, 
                    amount REAL, 
                    date TEXT)''')
    conn.commit()
    conn.close()

# User Authentication
def authenticate(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Account Management
def create_account(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        messagebox.showinfo('Success', 'Account created successfully')
    except sqlite3.IntegrityError:
        messagebox.showerror('Error', 'Username already exists')
    conn.close()

def deposit(username, amount):
    if amount <= 0:
        messagebox.showerror('Error', 'Amount must be greater than zero')
        return
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (amount, username))
    c.execute('INSERT INTO transactions (username, type, amount, date) VALUES (?, ?, ?, datetime("now"))', (username, 'Deposit', amount))
    conn.commit()
    conn.close()
    messagebox.showinfo('Success', 'Deposit successful')

def withdraw(username, amount):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT balance FROM users WHERE username = ?', (username,))
    balance = c.fetchone()[0]
    if amount <= 0:
        messagebox.showerror('Error', 'Amount must be greater than zero')
    elif amount > balance:
        messagebox.showerror('Error', 'Insufficient funds')
    else:
        c.execute('UPDATE users SET balance = balance - ? WHERE username = ?', (amount, username))
        c.execute('INSERT INTO transactions (username, type, amount, date) VALUES (?, ?, ?, datetime("now"))', (username, 'Withdraw', amount))
        conn.commit()
        messagebox.showinfo('Success', 'Withdrawal successful')
    conn.close()

def check_balance(username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT balance FROM users WHERE username = ?', (username,))
    balance = c.fetchone()[0]
    conn.close()
    return balance

def get_transaction_history(username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT type, amount, date FROM transactions WHERE username = ?', (username,))
    transactions = c.fetchall()
    conn.close()
    return transactions

# GUI Setup
class BankingApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Online Banking System')
        self.root.geometry('400x300')
        self.username = None

        self.create_login_frame()

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack()

        tk.Label(self.login_frame, text='Username').pack()
        self.login_username = tk.Entry(self.login_frame)
        self.login_username.pack()

        tk.Label(self.login_frame, text='Password').pack()
        self.login_password = tk.Entry(self.login_frame, show='*')
        self.login_password.pack()

        tk.Button(self.login_frame, text='Login', command=self.login).pack()
        tk.Button(self.login_frame, text='Create Account', command=self.create_account_frame).pack()

    def create_account_frame(self):
        self.login_frame.pack_forget()
        self.account_frame = tk.Frame(self.root)
        self.account_frame.pack()

        tk.Label(self.account_frame, text='Username').pack()
        self.account_username = tk.Entry(self.account_frame)
        self.account_username.pack()

        tk.Label(self.account_frame, text='Password').pack()
        self.account_password = tk.Entry(self.account_frame, show='*')
        self.account_password.pack()

        tk.Button(self.account_frame, text='Create', command=self.create_account).pack()
        tk.Button(self.account_frame, text='Back', command=self.back_to_login).pack()

    def back_to_login(self):
        self.account_frame.pack_forget()
        self.create_login_frame()

    def create_account(self):
        username = self.account_username.get()
        password = self.account_password.get()
        create_account(username, password)
        self.account_frame.pack_forget()
        self.create_login_frame()

    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()
        if authenticate(username, password):
            self.username = username
            self.login_frame.pack_forget()
            self.create_dashboard()
        else:
            messagebox.showerror('Error', 'Invalid credentials')

    def create_dashboard(self):
        self.dashboard_frame = tk.Frame(self.root)
        self.dashboard_frame.pack()

        tk.Button(self.dashboard_frame, text='Deposit', command=self.deposit_frame).pack()
        tk.Button(self.dashboard_frame, text='Withdraw', command=self.withdraw_frame).pack()
        tk.Button(self.dashboard_frame, text='Check Balance', command=self.check_balance).pack()
        tk.Button(self.dashboard_frame, text='Transaction History', command=self.transaction_history).pack()
        tk.Button(self.dashboard_frame, text='Logout', command=self.logout).pack()

    def deposit_frame(self):
        self.dashboard_frame.pack_forget()
        self.deposit_frame = tk.Frame(self.root)
        self.deposit_frame.pack()

        tk.Label(self.deposit_frame, text='Amount').pack()
        self.deposit_amount = tk.Entry(self.deposit_frame)
        self.deposit_amount.pack()

        tk.Button(self.deposit_frame, text='Deposit', command=self.deposit).pack()
        tk.Button(self.deposit_frame, text='Back', command=self.back_to_dashboard).pack()

    def deposit(self):
        amount = float(self.deposit_amount.get())
        deposit(self.username, amount)
        self.deposit_frame.pack_forget()
        self.create_dashboard()

    def withdraw_frame(self):
        self.dashboard_frame.pack_forget()
        self.withdraw_frame = tk.Frame(self.root)
        self.withdraw_frame.pack()

        tk.Label(self.withdraw_frame, text='Amount').pack()
        self.withdraw_amount = tk.Entry(self.withdraw_frame)
        self.withdraw_amount.pack()

        tk.Button(self.withdraw_frame, text='Withdraw', command=self.withdraw).pack()
        tk.Button(self.withdraw_frame, text='Back', command=self.back_to_dashboard).pack()

    def withdraw(self):
        amount = float(self.withdraw_amount.get())
        withdraw(self.username, amount)
        self.withdraw_frame.pack_forget()
        self.create_dashboard()

    def check_balance(self):
        balance = check_balance(self.username)
        messagebox.showinfo('Balance', f'Your balance is ${balance}')

    def transaction_history(self):
        transactions = get_transaction_history(self.username)
        transaction_str = "\n".join([f'{t[0]}: ${t[1]} on {t[2]}' for t in transactions])
        messagebox.showinfo('Transaction History', transaction_str)

    def logout(self):
        self.username = None
        self.dashboard_frame.pack_forget()
        self.create_login_frame()

    def back_to_dashboard(self):
        self.deposit_frame.pack_forget()
        self.withdraw_frame.pack_forget()
        self.create_dashboard()

if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = BankingApp(root)
    root.mainloop()
