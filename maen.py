import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
from datetime import datetime

DATA_FILE = "history.json"
API_URL = "https://api.exchangerate-api.com/v4/latest/"  # бесплатный ключ не требуется

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("700x500")

        # Загрузка истории
        self.history = []
        self.load_history()

        # Получение списка валют
        self.currencies = self.fetch_currencies()

        # Создание интерфейса
        self.create_widgets()
        self.update_history_display()

    def fetch_currencies(self):
        """Получает список доступных валют через API"""
        try:
            response = requests.get(API_URL + "USD")
            if response.status_code == 200:
                data = response.json()
                return sorted(data["rates"].keys())
            else:
                messagebox.showerror("Ошибка", "Не удалось получить список валют")
                return ["USD", "EUR", "RUB", "GBP"]  # запасной вариант
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {e}")
            return ["USD", "EUR", "RUB", "GBP"]

    def create_widgets(self):
        # Рамка для конвертации
        frame = tk.LabelFrame(self.root, text="Конвертация", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        tk.Label(frame, text="Сумма:").grid(row=0, column=0, sticky="e")
        self.amount_entry = tk.Entry(frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5)

        # Из валюты
        tk.Label(frame, text="Из валюты:").grid(row=0, column=2, sticky="e")
        self.from_currency = ttk.Combobox(frame, values=self.currencies, width=8)
        self.from_currency.grid(row=0, column=3, padx=5)
        self.from_currency.set("USD")

        # В валюту
        tk.Label(frame, text="В валюту:").grid(row=0, column=4, sticky="e")
        self.to_currency = ttk.Combobox(frame, values=self.currencies, width=8)
        self.to_currency.grid(row=0, column=5, padx=5)
        self.to_currency.set("EUR")

        # Кнопка конвертации
        self.convert_btn = tk.Button(frame, text="Конвертировать", command=self.convert, bg="lightblue")
        self.convert_btn.grid(row=1, column=0, columnspan=6, pady=10)

        # Результат
        self.result_label = tk.Label(frame, text="Результат: ", font=("Arial", 12, "bold"))
        self.result_label.grid(row=2, column=0, columnspan=6)

        # История
        history_frame = tk.LabelFrame(self.root, text="История конвертаций", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.history_tree = ttk.Treeview(history_frame, columns=("date", "amount", "from_curr", "to_curr", "result"), show="headings")
        self.history_tree.heading("date", text="Дата")
        self.history_tree.heading("amount", text="Сумма")
        self.history_tree.heading("from_curr", text="Из")
        self.history_tree.heading("to_curr", text="В")
        self.history_tree.heading("result", text="Результат")
        self.history_tree.column("date", width=130)
        self.history_tree.column("amount", width=100)
        self.history_tree.column("from_curr", width=60)
        self.history_tree.column("to_curr", width=60)
        self.history_tree.column("result", width=100)

        scroll = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scroll.set)
        self.history_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Кнопка очистки истории
        tk.Button(history_frame, text="Очистить историю", command=self.clear_history, bg="lightcoral").pack(pady=5)

    def convert(self):
        amount_str = self.amount_entry.get().strip()
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        # Валидация
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное числовое значение")
            return

        # Запрос к API
        try:
            response = requests.get(API_URL + from_curr)
            if response.status_code != 200:
                messagebox.showerror("Ошибка", "Не удалось получить курс валют")
                return
            data = response.json()
            rate = data["rates"].get(to_curr)
            if rate is None:
                messagebox.showerror("Ошибка", "Валюта не найдена")
                return
            result = amount * rate
            self.result_label.config(text=f"Результат: {result:.2f} {to_curr}")

            # Сохраняем в историю
            record = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amount,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "result": round(result, 2)
            }
            self.history.append(record)
            self.save_history()
            self.update_history_display()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {e}")

    def update_history_display(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for rec in reversed(self.history):  # от новых к старым
            self.history_tree.insert("", tk.END, values=(
                rec["date"],
                rec["amount"],
                rec["from_currency"],
                rec["to_currency"],
                rec["result"]
            ))

    def save_history(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def load_history(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        except FileNotFoundError:
            self.history = []

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
