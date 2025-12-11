import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
from typing import List, Dict, Tuple
import math

# ============================================================
#                    ЗАВДАННЯ 1 — ROD CUTTING
# ============================================================

S_COST = 10  # фіксована вартість стрижня (варіант 11)


def rod_cutting_memo(length: int, prices: List[int]) -> Dict:
    """
    Знаходить оптимальний спосіб розрізання через рекурсію з мемоізацією.
    Повертає словник:
      {
        "gross_profit": ...,
        "net_profit": ...,
        "pieces": [...],
        "cuts": ...
      }
    """
    if length <= 0 or len(prices) != length:
        raise ValueError("Довжина та кількість цін повинні збігатися і бути > 0.")

    memo: Dict[int, Tuple[int, List[int]]] = {}

    def helper(n: int) -> Tuple[int, List[int]]:
        if n == 0:
            return 0, []
        if n in memo:
            return memo[n]

        best_profit = -math.inf
        best_combo: List[int] = []

        # пробуємо всі можливі перші відрізки довжини i (1..n)
        for i in range(1, n + 1):
            price_i = prices[i - 1]
            remain_profit, remain_pieces = helper(n - i)
            total = price_i + remain_profit
            if total > best_profit:
                best_profit = total
                best_combo = [i] + remain_pieces

        memo[n] = (best_profit, best_combo)
        return memo[n]

    gross_profit, pieces = helper(length)
    net_profit = gross_profit - S_COST
    cuts = max(0, len(pieces) - 1)

    return {
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "pieces": pieces,
        "cuts": cuts,
    }


def rod_cutting_table(length: int, prices: List[int]) -> Dict:
    """
    Знаходить оптимальний спосіб розрізання через табуляцію.
    """
    if length <= 0 or len(prices) != length:
        raise ValueError("Довжина та кількість цін повинні збігатися і бути > 0.")

    # dp[i] — максимальний прибуток для довжини i
    dp = [0] * (length + 1)
    # choice[i] — довжина першого шматка для оптимального розбиття i
    choice = [0] * (length + 1)

    for n in range(1, length + 1):
        best_profit = -math.inf
        best_first = 0
        for i in range(1, n + 1):
            total = prices[i - 1] + dp[n - i]
            if total > best_profit:
                best_profit = total
                best_first = i
        dp[n] = best_profit
        choice[n] = best_first

    # Відновлення відрізків
    pieces: List[int] = []
    rem = length
    while rem > 0:
        p = choice[rem]
        pieces.append(p)
        rem -= p

    gross_profit = dp[length]
    net_profit = gross_profit - S_COST
    cuts = max(0, len(pieces) - 1)

    return {
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "pieces": pieces,
        "cuts": cuts,
    }


def run_rod_cutting():
    """Зчитує введення користувача та запускає обидва алгоритми DP."""
    try:
        length = int(entry_length.get())
    except ValueError:
        messagebox.showerror("Помилка", "Довжина повинна бути цілим числом.")
        return

    try:
        prices = list(map(int, entry_prices.get().split(",")))
    except Exception:
        messagebox.showerror("Помилка", "Ціни введіть у форматі: 2,5,7,8,10")
        return

    if len(prices) != length:
        messagebox.showerror("Помилка", "Кількість цін повинна дорівнювати довжині стрижня!")
        return

    try:
        res_memo = rod_cutting_memo(length, prices)
        res_tab = rod_cutting_table(length, prices)
    except Exception as e:
        messagebox.showerror("Помилка", str(e))
        return

    text = []
    text.append("=== Рекурсія з мемоізацією ===")
    text.append(f"Валовий прибуток: {res_memo['gross_profit']}")
    text.append(f"Чистий прибуток (мінус S={S_COST}): {res_memo['net_profit']}")
    text.append(f"Відрізки: {res_memo['pieces']}")
    text.append(f"Кількість розрізів: {res_memo['cuts']}")

    text.append("\n=== Табуляція ===")
    text.append(f"Валовий прибуток: {res_tab['gross_profit']}")
    text.append(f"Чистий прибуток (мінус S={S_COST}): {res_tab['net_profit']}")
    text.append(f"Відрізки: {res_tab['pieces']}")
    text.append(f"Кількість розрізів: {res_tab['cuts']}")

    messagebox.showinfo("Розрізання стрижня", "\n".join(text))


# ============================================================
#   ЗАВДАННЯ 2 — ОПТИМІЗАЦІЯ ЧЕРГИ 3D-ПРИНТЕРА (варіант 11)
# ============================================================

@dataclass
class PrintJob:
    id: str
    volume: float
    priority: int  # 1, 2, 3
    print_time: int  # хвилини


@dataclass
class PrinterConstraints:
    max_volume: float
    max_items: int


@dataclass
class Batch:
    jobs: List[PrintJob]

    @property
    def total_volume(self) -> float:
        return sum(j.volume for j in self.jobs)

    @property
    def has_p1(self) -> bool:
        return any(j.priority == 1 for j in self.jobs)

    @property
    def has_p3(self) -> bool:
        return any(j.priority == 3 for j in self.jobs)

    @property
    def time_without_penalty(self) -> int:
        return max(j.print_time for j in self.jobs) if self.jobs else 0

    @property
    def penalty(self) -> int:
        # Варіант 11: штраф 15 хв, якщо в партії змішані P1 та P3
        return 15 if self.has_p1 and self.has_p3 else 0

    @property
    def total_time(self) -> int:
        return self.time_without_penalty + self.penalty


def optimize_printing(print_jobs: List[PrintJob],
                      constraints: PrinterConstraints) -> Dict:
    """
    Жадібна оптимізація:
      - сортуємо задачі за пріоритетом (1 -> 2 -> 3), потім за часом друку (спадно);
      - додаємо в існуючі партії, не перевищуючи max_volume і max_items;
      - намагаємось не створювати партій зі змішаним пріоритетом P1+P3.
    """

    # Сортування: вищий пріоритет перший, при однаковому — довший друк спочатку
    jobs_sorted = sorted(print_jobs, key=lambda j: (j.priority, -j.print_time))

    batches: List[Batch] = []

    for job in jobs_sorted:
        placed = False

        # Спробуємо покласти завдання в існуючу партію
        for batch in batches:
            if batch.total_volume + job.volume > constraints.max_volume:
                continue
            if len(batch.jobs) + 1 > constraints.max_items:
                continue

            would_mixed_p1p3 = (
                (job.priority == 1 and batch.has_p3) or
                (job.priority == 3 and batch.has_p1)
            )
            if would_mixed_p1p3:
                # Уникаємо створення нової партії зі штрафом, якщо можливо
                continue

            batch.jobs.append(job)
            placed = True
            break

        if not placed:
            # Створюємо нову партію
            batches.append(Batch(jobs=[job]))

    total_time = sum(b.total_time for b in batches)
    print_order: List[str] = []
    for b in batches:
        for j in b.jobs:
            print_order.append(j.id)

    return {
        "print_order": print_order,
        "total_time": total_time,
        "batches": batches,
    }


def run_3d_printing():
    """Зчитує вхідні дані задач із текстового поля + обмеження принтера."""
    # Обмеження принтера
    try:
        max_volume = float(entry_max_volume.get())
        max_items = int(entry_max_items.get())
    except ValueError:
        messagebox.showerror("Помилка", "max_volume має бути числом, max_items — цілим.")
        return

    constraints = PrinterConstraints(max_volume=max_volume, max_items=max_items)

    # Зчитуємо задачі з текстового поля
    raw_text = text_jobs.get("1.0", "end").strip()
    if not raw_text:
        messagebox.showerror("Помилка", "Введіть хоча б одне завдання для друку.")
        return

    lines = raw_text.splitlines()
    jobs: List[PrintJob] = []

    try:
        for line in lines:
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 4:
                raise ValueError(
                    f"Рядок '{line}' має бути у форматі: id,об'єм,пріоритет,час"
                )
            jid = parts[0]
            vol = float(parts[1])
            prio = int(parts[2])
            ptime = int(parts[3])

            if prio not in (1, 2, 3):
                raise ValueError(f"Невірний пріоритет у рядку '{line}' (має бути 1, 2 або 3).")
            if vol <= 0 or ptime <= 0:
                raise ValueError(f"Об'єм і час друку мають бути > 0 у рядку '{line}'.")

            jobs.append(PrintJob(jid, vol, prio, ptime))
    except Exception as e:
        messagebox.showerror("Помилка при парсингу задач", str(e))
        return

    if not jobs:
        messagebox.showerror("Помилка", "Не вдалося створити жодного завдання.")
        return

    result = optimize_printing(jobs, constraints)

    text_lines = []
    text_lines.append("Оптимальний порядок друку:")
    text_lines.append(" -> ".join(result["print_order"]))
    text_lines.append(f"\nЗагальний час друку: {result['total_time']} хв")

    text_lines.append("\nПартії друку:")
    for i, batch in enumerate(result["batches"], start=1):
        ids = [j.id for j in batch.jobs]
        text_lines.append(
            f"Партія {i}: {ids}, час без штрафу={batch.time_without_penalty} хв, "
            f"штраф={batch.penalty} хв, разом={batch.total_time} хв"
        )

    messagebox.showinfo("Оптимізація 3D-друку", "\n".join(text_lines))


# ============================================================
#                           GUI
# ============================================================

def run_selected_task():
    if task_var.get() == "rod":
        run_rod_cutting()
    else:
        run_3d_printing()


root = tk.Tk()
root.title("Лабораторна робота №5")

# --- вибір завдання ---
tk.Label(root, text="Оберіть завдання:", font=("Arial", 14)).pack(pady=10)

task_var = tk.StringVar(value="rod")

tk.Radiobutton(
    root,
    text="Завдання 1: Розрізання стрижня (DP)",
    variable=task_var,
    value="rod"
).pack(anchor="w", padx=20)

tk.Radiobutton(
    root,
    text="Завдання 2: Оптимізація черги 3D-принтера",
    variable=task_var,
    value="print"
).pack(anchor="w", padx=20)

# --- Блок введення для Завдання 1 ---
frame1 = tk.LabelFrame(root, text="Дані для завдання 1", padx=10, pady=10)
frame1.pack(fill="x", padx=10, pady=10)

tk.Label(frame1, text="Довжина стрижня:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
entry_length = tk.Entry(frame1, width=10)
entry_length.grid(row=0, column=1, padx=5)

tk.Label(frame1, text="Ціни (через кому):", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
entry_prices = tk.Entry(frame1, width=25)
entry_prices.grid(row=1, column=1, padx=5)

# Можна одразу підставити приклад з умови
entry_length.insert(0, "5")
entry_prices.insert(0, "2,5,7,8,10")

# --- Блок введення для Завдання 2 ---
frame2 = tk.LabelFrame(root, text="Дані для завдання 2", padx=10, pady=10)
frame2.pack(fill="both", expand=True, padx=10, pady=10)

tk.Label(frame2, text="Завдання (по одному на рядок, формат: id,об'єм,пріоритет,час):",
         font=("Arial", 10)).pack(anchor="w")

text_jobs = tk.Text(frame2, width=50, height=8)
text_jobs.pack(pady=5)

# Приклад даних
example_jobs = (
    "M1,30,1,120\n"
    "M2,20,2,60\n"
    "M3,25,3,90\n"
    "M4,10,1,30\n"
    "M5,15,3,45\n"
)
text_jobs.insert("1.0", example_jobs)

frame_constraints = tk.Frame(frame2)
frame_constraints.pack(pady=5, anchor="w")

tk.Label(frame_constraints, text="max_volume:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
entry_max_volume = tk.Entry(frame_constraints, width=8)
entry_max_volume.grid(row=0, column=1, padx=5)

tk.Label(frame_constraints, text="max_items:", font=("Arial", 10)).grid(row=0, column=2, sticky="w")
entry_max_items = tk.Entry(frame_constraints, width=8)
entry_max_items.grid(row=0, column=3, padx=5)

entry_max_volume.insert(0, "60")
entry_max_items.insert(0, "3")

# --- кнопка запуску ---
tk.Button(root, text="Виконати", width=30, command=run_selected_task).pack(pady=15)

root.mainloop()
