import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

API_KEY = "YOUR_API_KEY_HERE"
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"

HISTORY_FILE = "history.json"


# ===== Работа с API =====
def get_rates(base_currency):
    try:
        response = requests.get(API_URL + base_currency)
        data = response.json()
        if data["result"] == "success":
            return data["conversion_rates"]
        else:
            messagebox.showerror("Ошибка", "Не удалось получить курсы валют")
            return None
    except Exception:
        messagebox.showerror("Ошибка", "Проблема с подключением к API")
        return None


# ===== История =====
def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def add_to_history(entry):
    history = load_history()
    history.append(entry)
    save_history(history)


# ===== Конвертация =====
def convert():
    amount = amount_entry.get()
    from_currency = from_combo.get()
    to_currency = to_combo.get()

    # Проверка ввода
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except:
        messagebox.showerror("Ошибка", "Введите положительное число")
        return

    rates = get_rates(from_currency)
    if not rates:
        return

    result = amount * rates[to_currency]
    result_label.config(text=f"Результат: {result:.2f} {to_currency}")

    # Сохранение в историю
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "result": result
    }

    add_to_history(entry)
    update_table()


# ===== Таблица =====
def update_table():
    for row in tree.get_children():
        tree.delete(row)

    history = load_history()
    for item in history:
        tree.insert("", "end", values=(
            item["date"],
            item["amount"],
            item["from"],
            item["to"],
            f"{item['result']:.2f}"
        ))


# ===== GUI =====
root = tk.Tk()
root.title("Currency Converter")
root.geometry("700x500")

currencies = ["USD", "EUR", "RUB", "RON", "GBP", "JPY"]

# Выбор валют
from_combo = ttk.Combobox(root, values=currencies)
from_combo.set("USD")
from_combo.pack()

to_combo = ttk.Combobox(root, values=currencies)
to_combo.set("EUR")
to_combo.pack()

# Поле ввода
amount_entry = tk.Entry(root)
amount_entry.pack()

# Кнопка
convert_btn = tk.Button(root, text="Конвертировать", command=convert)
convert_btn.pack()

# Результат
result_label = tk.Label(root, text="Результат:")
result_label.pack()

# Таблица
columns = ("Дата", "Сумма", "Из", "В", "Результат")
tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)

tree.pack(expand=True, fill="both")

update_table()

root.mainloop()