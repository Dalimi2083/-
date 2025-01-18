import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import date, timedelta
import os

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "records.json")


def load_data():
    """Загружает данные из JSON файла."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {}


def save_data(data):
    """Сохраняет данные в JSON файл."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


class StudentTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Отслеживание учеников")

        self.students = {
            "10А": [
                "Иванов Иван",
                "Петров Петр",
            ],
            "10Б": [
                "Сидоров Сидор",
                "Александров Александр",
                "Екатерина Катерина"
                
            ],
            "11А": [
               "Олег Олегов"
            ]
            # Добавьте больше учеников и классов по мере необходимости
        }
        self.flat_students = [f"{student} ({klass})" for klass in self.students for student in self.students[klass]]
        self.current_student = tk.StringVar()
        self.current_student.set(self.flat_students[0])
        self.selected_date = date.today()
        self.data = load_data()
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для выбора даты
        date_frame = tk.Frame(self.root)
        date_frame.pack(pady=10)

        tk.Button(date_frame, text="<", command=self.prev_day).grid(row=0, column=0, padx=5)
        self.date_label = tk.Label(date_frame, text=self.selected_date.isoformat())
        self.date_label.grid(row=0, column=1, padx=5)
        tk.Button(date_frame, text=">", command=self.next_day).grid(row=0, column=2, padx=5)

        # Поле поиска
        self.search_entry = ttk.Combobox(self.root, values=self.flat_students,width=30)
        self.search_entry.pack(pady=10)
        self.search_entry.set(self.flat_students[0])
        self.search_entry.bind('<KeyRelease>', self.check_search)

        # Кнопки
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack()

        self.forgot_button = tk.Button(buttons_frame, text="Забыл пропуск", command=lambda: self.mark_student("Забыл пропуск"))
        self.lost_button = tk.Button(buttons_frame, text="Потерял пропуск", command=lambda: self.mark_student("Потерял пропуск"))
        self.late_button = tk.Button(buttons_frame, text="Опоздал", command=lambda: self.mark_student("Опоздал"))
        self.shoes_button = tk.Button(buttons_frame, text="Забыл сменную обувь", command=lambda: self.mark_student("Забыл сменную обувь"))
        
        self.forgot_button.grid(row=0, column=0, padx=5, pady=5)
        self.lost_button.grid(row=0, column=1, padx=5, pady=5)
        self.late_button.grid(row=0, column=2, padx=5, pady=5)
        self.shoes_button.grid(row=0, column=3, padx=5, pady=5)

        # Дерево для отображения данных
        self.tree = ttk.Treeview(self.root, columns=("status"), show="headings")
        self.tree.heading("status", text="Статус")
        self.tree.column("status", width=400)
        self.tree.pack(pady=10)
        self.tree.bind("<Double-1>", self.edit_record)

        # Кнопка удаления записи
        tk.Button(self.root, text="Удалить запись", command=self.delete_record).pack(pady=5)

        # Вывод статуса
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=10)

        self.load_daily_data()

    def check_search(self, event):
        value = event.widget.get()
        if value == '':
           self.search_entry['values'] = self.flat_students
        else:
           data = []
           for item in self.flat_students:
                if value.lower() in item.lower():
                   data.append(item)
           self.search_entry['values'] = data

    def prev_day(self):
        """Переходит к предыдущему дню."""
        self.selected_date -= timedelta(days=1)
        self.date_label.config(text=self.selected_date.isoformat())
        self.load_daily_data()

    def next_day(self):
        """Переходит к следующему дню."""
        self.selected_date += timedelta(days=1)
        self.date_label.config(text=self.selected_date.isoformat())
        self.load_daily_data()

    def load_daily_data(self):
        """Загружает и отображает данные за выбранный день."""
        selected_date_str = self.selected_date.isoformat()
        print(selected_date_str)
        if selected_date_str in self.data:
            self.status_label.config(text=f"Данные за {selected_date_str} загружены.")
            self.populate_tree(self.data[selected_date_str])
        else:
            self.status_label.config(text=f"Нет данных за {selected_date_str}.")
            self.populate_tree({})
    
    def populate_tree(self, daily_data):
        """Очищает дерево и отображает данные за день."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for student, statuses in daily_data.items():
            for status in statuses:
                #self.tree.insert("", tk.END, values=(f"{student} - {status}"))
                val = f"{student} - {status}"
                print(val)
                self.tree.insert("", tk.END, values=[val])
    

    def mark_student(self, status):
        """Отмечает студента выбранным статусом."""
        selected_student = self.search_entry.get()
        selected_date_str = self.selected_date.isoformat()

        if selected_student:
           if selected_date_str not in self.data:
             self.data[selected_date_str] = {}
           
           if selected_student not in self.data[selected_date_str]:
             self.data[selected_date_str][selected_student] = []
           
           self.data[selected_date_str][selected_student].append(status)
           save_data(self.data)
           self.status_label.config(text=f"Отмечено: {selected_student} - {status}")
           self.load_daily_data()
        else:
           self.status_label.config(text="Не выбран студент.")

    def delete_record(self):
        """Удаляет выбранную запись из дерева и данных."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления.")
            return
        selected_date_str = self.selected_date.isoformat()
        selected_record = self.tree.item(selected_item, "values")[0]
        
        student_name = selected_record.split(" - ")[0]
        status = selected_record.split(" - ")[1]
    
        if selected_date_str in self.data and student_name in self.data[selected_date_str]:
           if status in self.data[selected_date_str][student_name]:
                self.data[selected_date_str][student_name].remove(status)
           
           if not self.data[selected_date_str][student_name]:
                del self.data[selected_date_str][student_name]
           
           if not self.data[selected_date_str]:
                del self.data[selected_date_str]
           
           save_data(self.data)
           self.load_daily_data()
           self.status_label.config(text="Запись удалена")
        else:
            messagebox.showerror("Ошибка", "Ошибка при удалении записи.")
    
    def edit_record(self, event):
      """Редактирует выбранную запись."""
      selected_item = self.tree.selection()
      if not selected_item:
          messagebox.showwarning("Предупреждение", "Выберите запись для редактирования.")
          return

      selected_date_str = self.selected_date.isoformat()
      selected_record = self.tree.item(selected_item, "values")[0]
      student_name = selected_record.split(" - ")[0]
      old_status = selected_record.split(" - ")[1]

      edit_window = tk.Toplevel(self.root)
      edit_window.title("Редактировать запись")

      status_label = tk.Label(edit_window, text="Выберите новый статус:")
      status_label.pack(pady=5)

      new_status = tk.StringVar(value=old_status)
      status_options = ["Забыл пропуск", "Потерял пропуск", "Опоздал", "Забыл сменную обувь"]
      status_menu = ttk.Combobox(edit_window, values=status_options, textvariable=new_status)
      status_menu.pack(pady=5)

      def save_edit():
            new_status_val = new_status.get()
            if selected_date_str in self.data and student_name in self.data[selected_date_str]:
                if old_status in self.data[selected_date_str][student_name]:
                    index = self.data[selected_date_str][student_name].index(old_status)
                    self.data[selected_date_str][student_name][index] = new_status_val
                    save_data(self.data)
                    self.load_daily_data()
                    self.status_label.config(text="Запись отредактирована")
                    edit_window.destroy()
                else:
                    messagebox.showerror("Ошибка", "Ошибка при редактировании записи.")
            else:
               messagebox.showerror("Ошибка", "Ошибка при редактировании записи.")

      save_button = tk.Button(edit_window, text="Сохранить", command=save_edit)
      save_button.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentTrackerApp(root)
    root.mainloop()
