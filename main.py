import tkinter as tk
from tkinter import ttk, messagebox
from db import add_task, get_tasks, delete_task, update_task, get_task_by_id
sort_buttons = {}

root = tk.Tk()
root.title("Task Manager")
root.geometry("800x600")

# === Top Button Panel ===
top_buttons = tk.Frame(root)
top_buttons.pack(pady=5)

form_visible = False
sort_visible = False
selected_task_id = None  # 🔸 для редагування

# === Task Table ===
task_tree = ttk.Treeview(root, columns=("ID", "Назва", "Пріоритет", "Створено"), show="headings")
for col in task_tree["columns"]:
    task_tree.heading(col, text=col)
task_tree.pack(fill="both", expand=True, padx=10)

# === Form Frame ===
form_frame = tk.Frame(root)

tk.Label(form_frame, text="Назва задачі:").pack()
title_entry = tk.Entry(form_frame, width=50)
title_entry.pack()

tk.Label(form_frame, text="Опис:").pack()
desc_entry = tk.Text(form_frame, width=50, height=5)
desc_entry.pack()

tk.Label(form_frame, text="Пріоритет (1-5):").pack()
priority_var = tk.StringVar()
priority_combo = ttk.Combobox(
    form_frame,
    textvariable=priority_var,
    values=[1, 2, 3, 4, 5],
    width=10,
    state="readonly"
)
priority_combo.pack()

tk.Button(form_frame, text="Зберегти", command=lambda: submit_task()).pack(pady=10)

# === Sort Frame ===
sort_frame = tk.Frame(root)

tk.Label(sort_frame, text="Сортувати за:", font=("Arial", 10, "bold")).pack(pady=5)

for name in ["Назва", "Пріоритет", "Створено"]:
    sort_buttons[name] = tk.Button(sort_frame, text=name, width=20,
                                   command=lambda col=name: sort_by_column(col))
    sort_buttons[name].pack(pady=2)

# === Управління формою/сортуванням ===

def toggle_form():
    global form_visible, sort_visible
    if sort_visible:
        toggle_sort()
    if form_visible:
        form_frame.pack_forget()
    else:
        form_frame.pack(fill="x", pady=10)
    form_visible = not form_visible

def toggle_sort():
    global sort_visible, form_visible
    if form_visible:
        toggle_form()
    if sort_visible:
        sort_frame.pack_forget()
    else:
        sort_frame.pack(fill="x", pady=10)
    sort_visible = not sort_visible

btn_add = tk.Button(top_buttons, text="Додати задачу", command=toggle_form)
btn_add.pack(side="left", padx=5)

btn_sort_toggle = tk.Button(top_buttons, text="Сортування", command=toggle_sort)
btn_sort_toggle.pack(side="left", padx=5)

btn_delete = tk.Button(top_buttons, text="Видалити", command=lambda: delete_selected())
btn_delete.pack(side="left", padx=5)

# === Додавання/Оновлення задачі ===
def submit_task():
    global selected_task_id
    title = title_entry.get()
    desc = desc_entry.get("1.0", tk.END).strip()
    priority = priority_var.get()

    if not title or not desc or not priority:
        messagebox.showerror("Помилка", "Усі поля мають бути заповнені!")
        return

    try:
        if selected_task_id:
            update_task(selected_task_id, title, desc, int(priority))
            messagebox.showinfo("Оновлено", f"Задачу #{selected_task_id} оновлено!")
            selected_task_id = None
        else:
            add_task(title, desc, int(priority))
            messagebox.showinfo("Успіх", "Задачу додано!")

        title_entry.delete(0, tk.END)
        desc_entry.delete("1.0", tk.END)
        priority_combo.set("")
        refresh_tasks()
        toggle_form()
    except Exception as e:
        messagebox.showerror("Помилка", str(e))

# === Видалення задачі ===
def delete_selected():
    global selected_task_id
    selected = task_tree.focus()
    if not selected:
        messagebox.showwarning("Увага", "Виберіть задачу для видалення.")
        return
    values = task_tree.item(selected, 'values')
    task_id = int(values[0])
    confirm = messagebox.askyesno("Підтвердження", f"Видалити задачу #{task_id}?")
    if confirm:
        delete_task(task_id)
        refresh_tasks()
        selected_task_id = None
        messagebox.showinfo("Видалено", "Задачу видалено.")

# === Обробка вибору для редагування ===
def on_row_select(event):
    global selected_task_id
    selected = task_tree.focus()
    if not selected:
        return
    values = task_tree.item(selected, 'values')
    selected_task_id = int(values[0])
    title_entry.delete(0, tk.END)
    title_entry.insert(0, values[1])
    priority_combo.set(values[2])
    desc_entry.delete("1.0", tk.END)
    task = get_task_by_id(selected_task_id)
    desc_entry.insert("1.0", task['description'])
    if not form_visible:
        toggle_form()

task_tree.bind("<<TreeviewSelect>>", on_row_select)

# === Сортування ===
sort_state = {"ID": False, "Назва": False, "Пріоритет": False, "Створено": False}

def refresh_tasks(sorted_by=None):
    for row in task_tree.get_children():
        task_tree.delete(row)
    data = get_tasks()
    if sorted_by:
        reverse = sort_state[sorted_by]
        key_map = {
            "Назва": "title",
            "Пріоритет": "priority",
            "Створено": "created_at"
        }
        data = sorted(data, key=lambda x: x[key_map[sorted_by]], reverse=reverse)
        sort_state[sorted_by] = not reverse

        # highlight active sort button
        for key, btn in sort_buttons.items():
            if key == sorted_by:
                btn.config(bg="#d0e0ff")
            else:
                btn.config(bg="SystemButtonFace")
    for task in data:
        task_tree.insert("", "end", values=(task['id'], task['title'], task['priority'], task['created_at']))

def sort_by_column(col):
    refresh_tasks(sorted_by=col)

# === Ініціалізація ===
refresh_tasks()
form_frame.pack_forget()
sort_frame.pack_forget()

root.mainloop()
