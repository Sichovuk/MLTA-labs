import tkinter as tk
from tkinter import messagebox

# -------------------------------------------------------------
#       1. МІНІМАЛЬНА КІЛЬКІСТЬ МОНЕТ (жадібний алгоритм)
# -------------------------------------------------------------

COINS = [50, 25, 10, 5]


def minimal_coins(n):
    if n < 0 or n > 1000:
        return "n має бути в межах 0 ≤ n ≤ 1000"

    result = []
    original_n = n

    for coin in COINS:
        count = n // coin
        if count > 0:
            result.append(f"{coin} коп — {count} шт.")
        n %= coin

    if n != 0:
        result.append(f"Неможливо видати {original_n} коп.")

    return "\n".join(result)


# -------------------------------------------------------------
#       2. РОЗКЛАДАННЯ n У СУМУ ПАРНИХ СТУПЕНІВ ДВІЙКИ
# -------------------------------------------------------------

def decompose_even_powers(n):
    if n < 1 or n > 1000:
        return "n має бути в межах 1 ≤ n ≤ 1000"

    result = []
    remaining = n

    powers = []
    p = 1
    while p <= n:
        powers.append(p)
        p *= 4
    powers.reverse()

    for p in powers:
        while remaining >= p:
            result.append(str(p))
            remaining -= p

    return "+".join(result)


# -------------------------------------------------------------
#                     GUI ФУНКЦІОНАЛ
# -------------------------------------------------------------

def run_algorithm():
    try:
        n = int(entry_n.get())
    except ValueError:
        messagebox.showerror("Помилка", "Введіть ціле число!")
        return

    algo = algo_var.get()

    if algo == "coins":
        result = minimal_coins(n)
        messagebox.showinfo("Мінімальний набір монет", result)

    elif algo == "powers":
        result = decompose_even_powers(n)
        messagebox.showinfo("Розклад у парні степені двійки", f"{n} = {result}")


# -------------------------------------------------------------
#                          GUI
# -------------------------------------------------------------

root = tk.Tk()
root.title("Лабораторна робота №4")

tk.Label(root, text="Оберіть завдання:", font=("Arial", 14)).pack(pady=10)

algo_var = tk.StringVar(value="coins")

tk.Radiobutton(root, text="1. Мінімальний набір монет", variable=algo_var, value="coins").pack()
tk.Radiobutton(root, text="2. Розклад числа у суму парних степенів двійки", variable=algo_var, value="powers").pack()

tk.Label(root, text="Введіть число n:", font=("Arial", 12)).pack(pady=10)
entry_n = tk.Entry(root, font=("Arial", 12))
entry_n.pack()

tk.Button(root, text="Виконати", width=30, command=run_algorithm).pack(pady=20)

root.mainloop()
