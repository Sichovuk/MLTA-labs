import tkinter as tk
from tkinter import messagebox
from collections import deque, defaultdict
import math

# Для візуалізації графа
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    HAS_NX = True
except Exception:
    HAS_NX = False


# ============================================================
#                 ЗАВДАННЯ 1 — MAX FLOW (Edmonds–Karp)
# ============================================================

def build_logistics_edges(include_variant_edge: bool):
    """
    Повертає список ребер (u, v, capacity).
    include_variant_edge=True додає ребро: Склад 3 -> Термінал 2 (10)
    """
    edges = [
        ("Термінал 1", "Склад 1", 25),
        ("Термінал 1", "Склад 2", 20),
        ("Термінал 1", "Склад 3", 15),

        ("Термінал 2", "Склад 3", 15),
        ("Термінал 2", "Склад 4", 30),
        ("Термінал 2", "Склад 2", 10),

        ("Склад 1", "Магазин 1", 15),
        ("Склад 1", "Магазин 2", 10),
        ("Склад 1", "Магазин 3", 20),

        ("Склад 2", "Магазин 4", 15),
        ("Склад 2", "Магазин 5", 10),
        ("Склад 2", "Магазин 6", 25),

        ("Склад 3", "Магазин 7", 20),
        ("Склад 3", "Магазин 8", 15),
        ("Склад 3", "Магазин 9", 10),

        ("Склад 4", "Магазин 10", 20),
        ("Склад 4", "Магазин 11", 10),
        ("Склад 4", "Магазин 12", 15),
        ("Склад 4", "Магазин 13", 5),
        ("Склад 4", "Магазин 14", 10),
    ]

    if include_variant_edge:
        edges.append(("Склад 3", "Термінал 2", 10))  # варіант

    return edges


def nodes_logistics():
    terminals = ["Термінал 1", "Термінал 2"]
    warehouses = ["Склад 1", "Склад 2", "Склад 3", "Склад 4"]
    shops = [f"Магазин {i}" for i in range(1, 15)]
    return terminals, warehouses, shops


def build_capacity_graph(edges, source, sink):
    """
    Будує capacity[u][v] (dict-of-dict), додає нульові зворотні ребра.
    """
    capacity = defaultdict(lambda: defaultdict(int))
    adj = defaultdict(list)

    def add_edge(u, v, c):
        if v not in adj[u]:
            adj[u].append(v)
        if u not in adj[v]:
            adj[v].append(u)  # для залишкової мережі
        capacity[u][v] += c  # якщо дубль — сумуємо

    for u, v, c in edges:
        add_edge(u, v, c)

    # переконаємось, що source/sink є в графі
    adj[source] = adj[source]
    adj[sink] = adj[sink]
    return capacity, adj


def edmonds_karp(capacity, adj, source, sink):
    """
    Edmonds–Karp: повертає (max_flow, flow, протокол_кроків)
    flow[u][v] — фактичний потік (зворотний зберігаємо як -flow[v][u]).
    """
    flow = defaultdict(lambda: defaultdict(int))
    steps = []
    max_flow = 0
    iteration = 0

    while True:
        iteration += 1
        parent = {source: None}
        q = deque([source])

        # BFS у залишковій мережі
        while q and sink not in parent:
            u = q.popleft()
            for v in adj[u]:
                residual = capacity[u][v] - flow[u][v]
                if residual > 0 and v not in parent:
                    parent[v] = u
                    q.append(v)

        if sink not in parent:
            steps.append(f"Зупинка: шляхів збільшення більше немає (ітерація {iteration}).")
            break

        # відновити шлях і знайти bottleneck
        path_nodes = []
        v = sink
        bottleneck = math.inf
        while v != source:
            u = parent[v]
            path_nodes.append(v)
            bottleneck = min(bottleneck, capacity[u][v] - flow[u][v])
            v = u
        path_nodes.append(source)
        path_nodes.reverse()

        # застосувати збільшення потоку
        v = sink
        while v != source:
            u = parent[v]
            flow[u][v] += bottleneck
            flow[v][u] -= bottleneck
            v = u

        max_flow += bottleneck
        steps.append(
            f"Крок {iteration}: шлях = {' → '.join(path_nodes)}, "
            f"Δ (bottleneck) = {bottleneck}, max_flow = {max_flow}"
        )

    return max_flow, flow, steps


def flow_decomposition_to_terminal_shop(flow, terminals, shops, super_source="SOURCE", super_sink="SINK"):
    """
    Розкладає потік на s-t шляхи (по позитивних flow[u][v] > 0) і агрегує:
      terminal -> shop -> amount
    Працює на графі з super_source, super_sink.
    """
    pos_flow = defaultdict(lambda: defaultdict(int))
    for u in flow:
        for v in flow[u]:
            if flow[u][v] > 0:
                pos_flow[u][v] = flow[u][v]

    table = {t: {s: 0 for s in shops} for t in terminals}

    def find_path():
        # DFS шлях SOURCE -> SINK по pos_flow
        stack = [(super_source, [super_source], {super_source})]
        while stack:
            u, path, seen = stack.pop()
            if u == super_sink:
                return path
            for v, fval in pos_flow[u].items():
                if fval > 0 and v not in seen:
                    stack.append((v, path + [v], seen | {v}))
        return None

    while True:
        path = find_path()
        if not path:
            break

        b = math.inf
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            b = min(b, pos_flow[u][v])

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            pos_flow[u][v] -= b

        terminal = path[1] if len(path) >= 3 and path[1] in terminals else None
        shop = path[-2] if len(path) >= 3 and path[-2] in shops else None

        if terminal and shop:
            table[terminal][shop] += b

    return table


def solve_logistics(include_variant_edge: bool):
    terminals, warehouses, shops = nodes_logistics()

    SOURCE = "SOURCE"
    SINK = "SINK"

    edges = build_logistics_edges(include_variant_edge)

    # SOURCE -> terminals (дуже великі)
    for t in terminals:
        edges.append((SOURCE, t, 10**9))

    # shops -> SINK (дуже великі)
    for s in shops:
        edges.append((s, SINK, 10**9))

    capacity, adj = build_capacity_graph(edges, SOURCE, SINK)
    max_flow, flow, steps = edmonds_karp(capacity, adj, SOURCE, SINK)

    table = flow_decomposition_to_terminal_shop(flow, terminals, shops, super_source=SOURCE, super_sink=SINK)

    terminal_totals = {t: max(0, flow[SOURCE][t]) for t in terminals}
    shop_totals = {s: max(0, flow[s][SINK]) for s in shops}

    return {
        "max_flow": max_flow,
        "steps": steps,
        "table": table,
        "terminal_totals": terminal_totals,
        "shop_totals": shop_totals,
        "edges_base": build_logistics_edges(include_variant_edge),
    }


def logistics_positions():
    pos = {}
    pos["Термінал 1"] = (-2.0, -1.0)
    pos["Термінал 2"] = (2.0, -1.0)

    pos["Склад 1"] = (-1.0, 0.0)
    pos["Склад 2"] = (1.0, 0.0)
    pos["Склад 3"] = (-1.5, -2.0)
    pos["Склад 4"] = (1.5, -2.0)

    for i in range(1, 7):
        pos[f"Магазин {i}"] = (-3.0 + (i - 1) * 1.2, 1.5)

    for i in range(7, 15):
        pos[f"Магазин {i}"] = (-3.3 + (i - 7) * 0.95, -3.5)

    return pos


def draw_logistics_graph(include_variant_edge: bool):
    if not HAS_NX:
        messagebox.showerror(
            "Помилка",
            "Не знайдено networkx/matplotlib.\n"
            "Встанови: pip install networkx matplotlib"
        )
        return

    edges = build_logistics_edges(include_variant_edge)
    G = nx.DiGraph()
    for u, v, c in edges:
        G.add_edge(u, v, capacity=c)

    pos = logistics_positions()
    plt.figure(figsize=(12, 6))
    nx.draw(
        G, pos, with_labels=True, node_size=1300, node_color="lightblue",
        arrows=True, arrowstyle='-|>', arrowsize=16, font_size=9
    )
    labels = {(u, v): d["capacity"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8)
    plt.title("Логістична мережа (Max Flow) — " + ("з варіантним ребром" if include_variant_edge else "базова"))
    plt.axis("off")
    plt.show()


# ============================================================
#                 ЗАВДАННЯ 2 — TRIE (Homework)
# ============================================================

class TrieNode:
    __slots__ = ("children", "is_end", "end_count")

    def __init__(self):
        self.children = {}
        self.is_end = False
        self.end_count = 0


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self._total_chars = 0
        self._words = []

    def put(self, word: str, value=None):
        if not isinstance(word, str):
            raise TypeError("word має бути рядком")
        if word == "":
            raise ValueError("Порожнє слово заборонено")

        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]

        if not node.is_end:
            node.is_end = True
        node.end_count += 1

        self._total_chars += len(word)
        self._words.append(word)


class Homework(Trie):
    def count_words_with_suffix(self, pattern) -> int:
        if not isinstance(pattern, str):
            raise TypeError("pattern має бути рядком")
        if pattern == "":
            return len(self._words)
        return sum(1 for w in self._words if w.endswith(pattern))

    def has_prefix(self, prefix) -> bool:
        if not isinstance(prefix, str):
            raise TypeError("prefix має бути рядком")
        if prefix == "":
            return len(self._words) > 0

        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def exists_with_mismatch(self, word, k) -> bool:
        if not isinstance(word, str):
            raise TypeError("word має бути рядком")
        if not isinstance(k, int):
            raise TypeError("k має бути цілим")
        if k < 0:
            raise ValueError("k має бути >= 0")
        if word == "":
            return False

        def dfs(node: TrieNode, i: int, mism: int) -> bool:
            if mism > k:
                return False
            if i == len(word):
                return node.is_end
            ch = word[i]
            for nxt_ch, nxt_node in node.children.items():
                new_mism = mism + (0 if nxt_ch == ch else 1)
                if dfs(nxt_node, i + 1, new_mism):
                    return True
            return False

        return dfs(self.root, 0, 0)

    def total_characters(self) -> int:
        return self._total_chars


# ============================================================
#                         GUI HELPERS
# ============================================================

def show_text_window(title: str, text: str):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("900x600")

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True)

    txt = tk.Text(frame, wrap="word")
    txt.pack(side="left", fill="both", expand=True)

    sb = tk.Scrollbar(frame, command=txt.yview)
    sb.pack(side="right", fill="y")
    txt.configure(yscrollcommand=sb.set)

    txt.insert("1.0", text)
    txt.configure(state="disabled")


# ============================================================
#                             GUI
# ============================================================

def run_maxflow_base():
    res = solve_logistics(include_variant_edge=False)

    terminals, _, shops = nodes_logistics()
    lines = []
    lines.append("=== Edmonds–Karp (БАЗОВА МЕРЕЖА) ===")
    lines.append(f"Максимальний потік = {res['max_flow']}\n")

    lines.append("Покроковий протокол (augmenting paths):")
    lines.extend(res["steps"])
    lines.append("\n")

    lines.append("Таблиця: Термінал → Магазин → Фактичний потік")
    lines.append("Термінал\tМагазин\tПотік")
    for t in terminals:
        for s in shops:
            lines.append(f"{t}\t{s}\t{res['table'][t][s]}")

    lines.append("\nПідсумок по терміналах (скільки відвантажили):")
    for t, val in res["terminal_totals"].items():
        lines.append(f"{t}: {val}")

    lines.append("\nПідсумок по магазинах (скільки отримали):")
    for s, val in res["shop_totals"].items():
        lines.append(f"{s}: {val}")

    # ====== ОНОВЛЕНО: Вивести ВСІ магазини з мінімальним потоком ======
    min_val = min(res["shop_totals"].values())
    min_shops = [s for s, v in res["shop_totals"].items() if v == min_val]

    lines.append("\nНайменше отримали:")
    lines.append(f"Мінімальний потік = {min_val}")
    lines.append("Список магазинів: " + ", ".join(min_shops))
    # ================================================================

    show_text_window("Max Flow — базова мережа", "\n".join(lines))


def run_maxflow_variant():
    res_base = solve_logistics(include_variant_edge=False)
    res_var = solve_logistics(include_variant_edge=True)

    lines = []
    lines.append("=== ПОРІВНЯННЯ: БАЗОВА vs ВАРІАНТ (Склад 3 → Термінал 2, 10) ===\n")
    lines.append(f"MaxFlow (базова)  = {res_base['max_flow']}")
    lines.append(f"MaxFlow (варіант) = {res_var['max_flow']}\n")

    if res_var["max_flow"] > res_base["max_flow"]:
        lines.append("ВИСНОВОК: зворотне ребро ЗБІЛЬШИЛО максимальний потік.")
    elif res_var["max_flow"] < res_base["max_flow"]:
        lines.append("ВИСНОВОК: зворотне ребро ЗМЕНШИЛО максимальний потік (нетипово для додавання ребра).")
    else:
        lines.append("ВИСНОВОК: зворотне ребро НЕ ВПЛИНУЛО на величину максимального потоку.")

    lines.append("\nПояснення (ідея):")
    lines.append("- Додавання ребра може створити додаткові маршрути у залишковій мережі.")
    lines.append("- Але якщо вузькі місця (bottlenecks) залишаються на інших ребрах,")
    lines.append("  то загальний max flow не зростає.")
    lines.append("- Якщо ж нове ребро дозволяє обійти вузьке місце — max flow зросте.\n")

    lines.append("Покроковий протокол (базова):")
    lines.extend(res_base["steps"])
    lines.append("\nПокроковий протокол (варіант):")
    lines.extend(res_var["steps"])

    show_text_window("Max Flow — порівняння", "\n".join(lines))


def draw_base_graph():
    draw_logistics_graph(include_variant_edge=False)


def draw_variant_graph():
    draw_logistics_graph(include_variant_edge=True)


# ----- Trie GUI -----
trie_obj = Homework()

def trie_add_words():
    raw = entry_words.get().strip()
    if not raw:
        messagebox.showerror("Помилка", "Введіть слова через кому або пробіл.")
        return

    parts = [p.strip() for p in raw.replace(",", " ").split()]
    added = 0
    for w in parts:
        if not w:
            continue
        try:
            trie_obj.put(w, added)
            added += 1
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося додати '{w}': {e}")
            return

    messagebox.showinfo("Trie", f"Додано слів: {added}\nЗараз у Trie слів: {len(trie_obj._words)}")


def trie_check_prefix():
    pref = entry_prefix.get()
    try:
        ok = trie_obj.has_prefix(pref)
    except Exception as e:
        messagebox.showerror("Помилка", str(e))
        return
    messagebox.showinfo("has_prefix", f"prefix='{pref}' -> {ok}")


def trie_count_suffix():
    suf = entry_suffix.get()
    try:
        cnt = trie_obj.count_words_with_suffix(suf)
    except Exception as e:
        messagebox.showerror("Помилка", str(e))
        return
    messagebox.showinfo("count_words_with_suffix", f"suffix='{suf}' -> {cnt}")


def trie_exists_mismatch():
    w = entry_mismatch_word.get()
    try:
        k = int(entry_mismatch_k.get())
    except ValueError:
        messagebox.showerror("Помилка", "k має бути цілим числом.")
        return
    try:
        ok = trie_obj.exists_with_mismatch(w, k)
    except Exception as e:
        messagebox.showerror("Помилка", str(e))
        return
    messagebox.showinfo("exists_with_mismatch", f"word='{w}', k={k} -> {ok}")


def trie_total_chars():
    messagebox.showinfo("total_characters", f"Загальна кількість символів у всіх словах = {trie_obj.total_characters()}")


def trie_load_sample():
    sample = ["apple", "application", "banana", "cat"]
    for i, w in enumerate(sample):
        trie_obj.put(w, i)
    messagebox.showinfo("Trie", "Завантажено приклад:\napple, application, banana, cat")


def run_selected_lab6_task():
    if task_var.get() == "maxflow":
        run_maxflow_base()
    else:
        messagebox.showinfo("Trie", "Використай кнопки у блоці Trie для перевірок.")


# ============================================================
#                          GUI LAYOUT
# ============================================================

root = tk.Tk()
root.title("Лабораторна робота №6 — Max Flow & Trie")
root.geometry("1000x700")

task_var = tk.StringVar(value="maxflow")

top = tk.Frame(root)
top.pack(fill="x", padx=10, pady=10)

tk.Label(top, text="Оберіть завдання:", font=("Arial", 14)).pack(anchor="w")
tk.Radiobutton(top, text="Завдання 1: Логістична мережа (Max Flow, Edmonds–Karp)",
               variable=task_var, value="maxflow").pack(anchor="w")
tk.Radiobutton(top, text="Завдання 2: Trie (prefix/suffix + варіантні методи)",
               variable=task_var, value="trie").pack(anchor="w")

tk.Button(top, text="Показати результат (для вибраного завдання)", width=50,
          command=run_selected_lab6_task).pack(pady=8)

# ---- Max Flow block ----
frame_flow = tk.LabelFrame(root, text="Завдання 1 — Max Flow", padx=10, pady=10)
frame_flow.pack(fill="x", padx=10, pady=10)

row1 = tk.Frame(frame_flow)
row1.pack(fill="x", pady=5)

tk.Button(row1, text="Запустити Edmonds–Karp (базова мережа)", width=40,
          command=run_maxflow_base).pack(side="left", padx=5)
tk.Button(row1, text="Порівняти базову vs варіант (Склад3→Терм2,10)", width=45,
          command=run_maxflow_variant).pack(side="left", padx=5)

row2 = tk.Frame(frame_flow)
row2.pack(fill="x", pady=5)

tk.Button(row2, text="Показати граф (базовий)", width=40,
          command=draw_base_graph).pack(side="left", padx=5)
tk.Button(row2, text="Показати граф (з варіантним ребром)", width=45,
          command=draw_variant_graph).pack(side="left", padx=5)

tk.Label(frame_flow, text=(
    "Після запуску відкриється вікно з протоколом:\n"
    "- кожен крок Edmonds–Karp показує знайдений шлях та Δ (bottleneck)\n"
    "- нижче є таблиця фактичних потоків Термінал→Магазин (через розклад потоку на шляхи)\n"
), justify="left").pack(anchor="w", pady=5)

# ---- Trie block ----
frame_trie = tk.LabelFrame(root, text="Завдання 2 — Trie (Homework)", padx=10, pady=10)
frame_trie.pack(fill="both", expand=True, padx=10, pady=10)

tk.Label(frame_trie, text="Додати слова (через кому або пробіл):").grid(row=0, column=0, sticky="w")
entry_words = tk.Entry(frame_trie, width=60)
entry_words.grid(row=0, column=1, padx=5, pady=2, sticky="w")
tk.Button(frame_trie, text="Додати", command=trie_add_words).grid(row=0, column=2, padx=5)

tk.Button(frame_trie, text="Завантажити приклад (apple, application, banana, cat)", command=trie_load_sample)\
  .grid(row=1, column=0, columnspan=3, sticky="w", pady=4)

tk.Label(frame_trie, text="has_prefix(prefix):").grid(row=2, column=0, sticky="w")
entry_prefix = tk.Entry(frame_trie, width=30)
entry_prefix.grid(row=2, column=1, sticky="w", padx=5)
tk.Button(frame_trie, text="Перевірити", command=trie_check_prefix).grid(row=2, column=2, padx=5)

tk.Label(frame_trie, text="count_words_with_suffix(pattern):").grid(row=3, column=0, sticky="w")
entry_suffix = tk.Entry(frame_trie, width=30)
entry_suffix.grid(row=3, column=1, sticky="w", padx=5)
tk.Button(frame_trie, text="Порахувати", command=trie_count_suffix).grid(row=3, column=2, padx=5)

tk.Label(frame_trie, text="exists_with_mismatch(word, k):").grid(row=4, column=0, sticky="w")
row_mis = tk.Frame(frame_trie)
row_mis.grid(row=4, column=1, sticky="w", padx=5)
entry_mismatch_word = tk.Entry(row_mis, width=25)
entry_mismatch_word.pack(side="left")
tk.Label(row_mis, text="k=").pack(side="left", padx=5)
entry_mismatch_k = tk.Entry(row_mis, width=5)
entry_mismatch_k.pack(side="left")
entry_mismatch_k.insert(0, "1")
tk.Button(frame_trie, text="Перевірити", command=trie_exists_mismatch).grid(row=4, column=2, padx=5)

tk.Button(frame_trie, text="total_characters()", command=trie_total_chars)\
  .grid(row=5, column=0, columnspan=3, sticky="w", pady=6)

tk.Label(frame_trie, text=(
    "Пояснення:\n"
    "- has_prefix: перевіряє шлях у Trie по символах префікса.\n"
    "- count_words_with_suffix: рахує слова, що закінчуються на pattern (враховує регістр).\n"
    "- exists_with_mismatch(word,k): шукає слово тієї ж довжини з ≤k невідповідними символами.\n"
    "- total_characters: сума довжин усіх доданих слів (з урахуванням повторів вставки).\n"
), justify="left").grid(row=6, column=0, columnspan=3, sticky="w", pady=8)

root.mainloop()
