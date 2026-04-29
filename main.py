import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime


class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.filename = 'weather_data.json'
        self.data = self.load_data()

        # --- Интерфейс ввода ---
        frame_input = tk.LabelFrame(root, text="Новая запись", padx=10, pady=10)
        frame_input.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_input, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0)
        self.entry_date = tk.Entry(frame_input)
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.entry_date.grid(row=0, column=1)

        tk.Label(frame_input, text="Температура (°C):").grid(row=0, column=2)
        self.entry_temp = tk.Entry(frame_input)
        self.entry_temp.grid(row=0, column=3)

        tk.Label(frame_input, text="Описание:").grid(row=1, column=0)
        self.entry_desc = tk.Entry(frame_input)
        self.entry_desc.grid(row=1, column=1)

        tk.Label(frame_input, text="Осадки:").grid(row=1, column=2)
        self.var_precip = tk.StringVar(value="Нет")
        self.combo_precip = ttk.Combobox(frame_input, textvariable=self.var_precip, values=["Да", "Нет"],
                                         state="readonly")
        self.combo_precip.grid(row=1, column=3)

        btn_add = tk.Button(frame_input, text="Добавить запись", command=self.add_entry, bg="#e1f5fe")
        btn_add.grid(row=2, column=0, columnspan=4, pady=10)

        # --- Интерфейс фильтрации ---
        frame_filter = tk.LabelFrame(root, text="Фильтрация", padx=10, pady=10)
        frame_filter.pack(padx=10, pady=5, fill="x")

        tk.Button(frame_filter, text="Показать всё", command=self.display_data).pack(side="left", padx=5)
        tk.Button(frame_filter, text="Температура > +10°C", command=lambda: self.filter_data('temp')).pack(side="left",
                                                                                                           padx=5)

        tk.Label(frame_filter, text="Поиск по дате:").pack(side="left", padx=5)
        self.entry_filter_date = tk.Entry(frame_filter, width=12)
        self.entry_filter_date.pack(side="left")
        tk.Button(frame_filter, text="Найти", command=lambda: self.filter_data('date')).pack(side="left", padx=2)

        # --- Таблица данных ---
        self.tree = ttk.Treeview(root, columns=("Date", "Temp", "Desc", "Precip"), show='headings')
        self.tree.heading("Date", text="Дата")
        self.tree.heading("Temp", text="Температура")
        self.tree.heading("Desc", text="Описание")
        self.tree.heading("Precip", text="Осадки")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.display_data()

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def validate(self):
        # 1. Валидация даты
        try:
            datetime.strptime(self.entry_date.get(), "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return False
        # 2. Валидация температуры
        try:
            float(self.entry_temp.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return False
        # 3. Валидация описания
        if not self.entry_desc.get().strip():
            messagebox.showerror("Ошибка", "Описание не может быть пустым!")
            return False
        return True

    def add_entry(self):
        if self.validate():
            new_entry = {
                "date": self.entry_date.get(),
                "temp": float(self.entry_temp.get()),
                "desc": self.entry_desc.get(),
                "precip": self.var_precip.get()
                15: 22
            }
            self.data.append(new_entry)
            self.save_data()
            self.display_data()
            self.entry_temp.delete(0, tk.END)
            self.entry_desc.delete(0, tk.END)

    def display_data(self, records=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        display_list = records if records is not None else self.data
        for r in display_list:
            self.tree.insert("", "end", values=(r["date"], r["temp"], r["desc"], r["precip"]))

    def filter_data(self, mode):
        if mode == 'temp':
            filtered = [r for r in self.data if r["temp"] > 10]
        elif mode == 'date':
            search_date = self.entry_filter_date.get()
            filtered = [r for r in self.data if search_date in r["date"]]
        self.display_data(filtered)


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()
