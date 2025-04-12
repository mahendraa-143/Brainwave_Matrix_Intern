import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import datetime

# --- Initialize Database ---
def init_db():
    with sqlite3.connect("inventory.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT NOT NULL)")
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
            product_id INTEGER,
            quantity_sold INTEGER,
            sale_amount REAL,
            sale_date TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        if cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            cursor.execute("INSERT INTO users VALUES (?, ?)", ("mahendra", "mahi"))

# --- Database Functions ---
def authenticate(username, password):
    with sqlite3.connect("inventory.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return cursor.fetchone()

def get_products():
    with sqlite3.connect("inventory.db") as conn:
        return conn.execute("SELECT * FROM products").fetchall()

def add_product(name, qty, price):
    with sqlite3.connect("inventory.db") as conn:
        conn.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))

def update_product(product_id, qty, price):
    with sqlite3.connect("inventory.db") as conn:
        conn.execute("UPDATE products SET quantity=?, price=? WHERE id=?", (qty, price, product_id))

def delete_product(product_id):
    with sqlite3.connect("inventory.db") as conn:
        conn.execute("DELETE FROM products WHERE id=?", (product_id,))

def record_sale(product_id, qty_sold, price):
    with sqlite3.connect("inventory.db") as conn:
        conn.execute("INSERT INTO sales (product_id, quantity_sold, sale_amount) VALUES (?, ?, ?)",
                     (product_id, qty_sold, qty_sold * price))
        conn.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (qty_sold, product_id))

def get_low_stock(threshold=5):
    with sqlite3.connect("inventory.db") as conn:
        return conn.execute("SELECT * FROM products WHERE quantity < ?", (threshold,)).fetchall()

def get_sales_summary():
    with sqlite3.connect("inventory.db") as conn:
        return conn.execute("SELECT p.name, SUM(s.quantity_sold), SUM(s.sale_amount) FROM sales s JOIN products p ON s.product_id = p.id GROUP BY s.product_id").fetchall()

# --- GUI Functions ---
def login():
    if authenticate(user_entry.get(), pass_entry.get()):
        login_frame.pack_forget()
        update_dropdown()
        load_table()
        main_frame.pack()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def update_dropdown():
    product_list = get_products()
    dropdown['values'] = [f"{p[0]} - {p[1]}" for p in product_list]
    if product_list:
        dropdown.current(0)
        fill_product_details()

def get_selected_product():
    try:
        selected = dropdown.get()
        return int(selected.split(" - ")[0])
    except:
        return None

def load_table():
    for row in table.get_children():
        table.delete(row)
    for product in get_products():
        tag = "low" if product[2] < int(low_stock_threshold.get() or 5) else ""
        table.insert("", "end", values=product, tags=(tag,))
    table.tag_configure("low", background="lightcoral")

def add_product_gui():
    try:
        name = name_entry.get()
        qty = int(qty_entry.get())
        price = float(price_entry.get())
        if not name or qty < 0 or price < 0:
            raise ValueError
        add_product(name, qty, price)
        update_dropdown()
        load_table()
        messagebox.showinfo("Added", "Product added successfully.")
    except:
        messagebox.showerror("Error", "Invalid input.")

def edit_product_gui():
    product_id = get_selected_product()
    if not product_id:
        return messagebox.showwarning("Select", "Select a product first.")
    try:
        qty = int(qty_entry.get())
        price = float(price_entry.get())
        if qty < 0 or price < 0:
            raise ValueError
        update_product(product_id, qty, price)
        update_dropdown()
        load_table()
        messagebox.showinfo("Updated", "Product updated successfully.")
    except:
        messagebox.showerror("Error", "Invalid quantity or price.")

def delete_product_gui():
    product_id = get_selected_product()
    if not product_id:
        return messagebox.showwarning("Select", "Select a product first.")
    delete_product(product_id)
    update_dropdown()
    load_table()
    messagebox.showinfo("Deleted", "Product deleted.")

def record_sale_gui():
    product_id = get_selected_product()
    if not product_id:
        return messagebox.showwarning("Select", "Select a product.")
    try:
        qty = int(sale_qty.get())
        if qty <= 0:
            raise ValueError("Quantity must be greater than zero.")
        with sqlite3.connect("inventory.db") as conn:
            available, price = conn.execute("SELECT quantity, price FROM products WHERE id=?", (product_id,)).fetchone()
        if qty > available:
            return messagebox.showerror("Error", f"Only {available} in stock.")
        record_sale(product_id, qty, price)
        update_dropdown()
        load_table()
        sale_qty.delete(0, tk.END)
        messagebox.showinfo("Sale", "Sale recorded.")
    except ValueError as ve:
        messagebox.showerror("Invalid Quantity", str(ve))
    except:
        messagebox.showerror("Error", "Please enter a valid quantity.")

def show_low_stock():
    try:
        threshold = int(low_stock_threshold.get())
        if threshold < 0:
            raise ValueError
    except:
        return messagebox.showerror("Invalid Input", "Please enter a valid threshold.")

    data = get_low_stock(threshold)
    report = "\n".join([f"{x[1]}: {x[2]} left" for x in data]) or "All items in stock."
    messagebox.showinfo("Low Stock Report", report)

    # Log to file
    with open("low_stock_log.txt", "a") as f:
        f.write(f"\n--- Low Stock Report ({datetime.datetime.now()}) ---\n")
        if data:
            for item in data:
                f.write(f"{item[1]}: {item[2]} left\n")
        else:
            f.write("All items in stock.\n")

def show_sales_summary():
    data = get_sales_summary()
    report = "\n".join([f"{x[0]} - Sold: {x[1]}, Revenue: ₹{x[2]:.2f}" for x in data]) or "No sales yet."
    messagebox.showinfo("Sales Summary", report)

def fill_product_details(event=None):
    product_id = get_selected_product()
    if not product_id:
        return
    with sqlite3.connect("inventory.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, quantity, price FROM products WHERE id=?", (product_id,))
        result = cursor.fetchone()
        if result:
            name_entry.delete(0, tk.END)
            name_entry.insert(0, result[0])
            qty_entry.delete(0, tk.END)
            qty_entry.insert(0, result[1])
            price_entry.delete(0, tk.END)
            price_entry.insert(0, result[2])
            sale_qty.delete(0, tk.END)

# --- GUI Setup ---
root = tk.Tk()
root.title("Inventory Manager")
root.geometry("700x650")

# --- Login Frame ---
login_frame = tk.Frame(root)
tk.Label(login_frame, text="Username").pack()
user_entry = tk.Entry(login_frame)
user_entry.pack()
tk.Label(login_frame, text="Password").pack()
pass_entry = tk.Entry(login_frame, show="*")
pass_entry.pack()
tk.Button(login_frame, text="Login", command=login).pack(pady=10)
login_frame.pack()

# --- Main Frame ---
main_frame = tk.Frame(root)

tk.Label(main_frame, text="Product Name").pack()
name_entry = tk.Entry(main_frame)
name_entry.pack()

tk.Label(main_frame, text="Quantity").pack()
qty_entry = tk.Entry(main_frame)
qty_entry.pack()

tk.Label(main_frame, text="Price").pack()
price_entry = tk.Entry(main_frame)
price_entry.pack()

tk.Button(main_frame, text="Add Product", command=add_product_gui).pack(pady=5)

tk.Label(main_frame, text="Select Product").pack()
dropdown = ttk.Combobox(main_frame, state="readonly")
dropdown.pack()
dropdown.bind("<<ComboboxSelected>>", fill_product_details)

tk.Button(main_frame, text="Edit Product", command=edit_product_gui).pack()
tk.Button(main_frame, text="Delete Product", command=delete_product_gui).pack()

tk.Label(main_frame, text="Quantity to Sell").pack()
sale_qty = tk.Entry(main_frame)
sale_qty.pack()
tk.Button(main_frame, text="Record Sale", command=record_sale_gui).pack(pady=5)

tk.Label(main_frame, text="Low Stock Threshold").pack()
low_stock_threshold = tk.Entry(main_frame)
low_stock_threshold.insert(0, "5")
low_stock_threshold.pack()

tk.Button(main_frame, text="Low Stock Report", command=show_low_stock).pack(pady=5)
tk.Button(main_frame, text="Sales Summary", command=show_sales_summary).pack(pady=5)

# --- Product Table ---
table = ttk.Treeview(main_frame, columns=("ID", "Name", "Qty", "Price"), show="headings")
for col in ("ID", "Name", "Qty", "Price"):
    table.heading(col, text=col)
    table.column(col, width=150)
table.pack(pady=10, fill=tk.BOTH, expand=True)

# --- Start App ---
init_db()
root.mainloop()
