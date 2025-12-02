import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import networkx as nx
import math

# -------------------------------------------------------------
#                      ГРАФ ДЛЯ ЛР №3
# -------------------------------------------------------------

VERTICES = ['a', 'b', 'c', 'd', 'e', 'f']

# (u, v, w) — ребро u→v з вагою w
EDGES = [
    ('a', 'b', 6),
    ('a', 'c', 2),
    ('a', 'e', 8),
    ('c', 'b', 3),
    ('b', 'f', 4),
    ('e', 'f', 1),
    ('e', 'd', 7),
    ('f', 'd', 2),
]

# -------------------------------------------------------------
#                   КООРДИНАТИ ВЕРШИН
# -------------------------------------------------------------

pos = {
    'a': (-0.400,  0.500),
    'b': ( 0.400,  0.500),
    'c': ( 0.000,  0.100),
    'e': (-0.600, -0.500),
    'f': ( 0.600, -0.500),
    'd': ( 0.000, -0.700),
}

# -------------------------------------------------------------
#              АЛГОРИТМ ДЕЙКСТРИ
# -------------------------------------------------------------

def dijkstra(start):
    dist = {v: math.inf for v in VERTICES}
    dist[start] = 0
    visited = set()
    protocol = []

    while len(visited) < len(VERTICES):
        # вибрати найближчу вершину
        u = None
        min_dist = math.inf
        for v in VERTICES:
            if v not in visited and dist[v] < min_dist:
                min_dist = dist[v]
                u = v

        if u is None:
            break

        visited.add(u)
        protocol.append(f"Вибрана вершина: {u}, dist={dist[u]}, S={visited.copy()}")

        # релаксація
        for (x, y, w) in EDGES:
            if x == u:
                if dist[y] > dist[u] + w:
                    old = dist[y]
                    dist[y] = dist[u] + w
                    protocol.append(f"Оновлення: dist[{y}] = {old} → {dist[y]}")

    return dist, protocol


# -------------------------------------------------------------
#       АЛГОРИТМ ФЛОЙДА–УОРШЕЛА
# -------------------------------------------------------------

def floyd_warshall():
    n = len(VERTICES)
    idx = {v: i for i, v in enumerate(VERTICES)}

    # ініціалізація матриці
    D = [[math.inf]*n for _ in range(n)]
    for v in VERTICES:
        D[idx[v]][idx[v]] = 0

    for u, v, w in EDGES:
        D[idx[u]][idx[v]] = w

    protocol = []

    # головний цикл алгоритму
    for k in range(n):
        protocol.append(f"\n=== Проміжна вершина: {VERTICES[k]} ===")
        for i in range(n):
            for j in range(n):
                old = D[i][j]
                if D[i][j] > D[i][k] + D[k][j]:
                    D[i][j] = D[i][k] + D[k][j]
                    protocol.append(
                        f"D[{VERTICES[i]}][{VERTICES[j]}] : {old} → {D[i][j]}"
                    )

    return D, protocol


# -------------------------------------------------------------
#                  ВІЗУАЛІЗАЦІЯ ГРАФУ
# -------------------------------------------------------------

def draw_graph():
    G = nx.DiGraph()
    for u, v, w in EDGES:
        G.add_edge(u, v, weight=w)

    plt.figure(figsize=(7, 7))
    nx.draw(
        G, pos,
        with_labels=True,
        node_size=1300,
        node_color="lightblue",
        arrows=True,
        arrowstyle='-|>',
        arrowsize=20,
        font_size=14
    )
    labels = {(u, v): w for (u, v, w) in EDGES}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=12)

    plt.title("Граф з вагами (Лабораторна №3)")
    plt.show()


# -------------------------------------------------------------
#                  ОБРОБКА КНОПОК GUI
# -------------------------------------------------------------

def run_dijkstra():
    dist, prot = dijkstra("a")
    text = "\n".join(prot)
    text += "\n\nНайкоротші відстані від a:\n"
    for v in sorted(dist):
        text += f"{v}: {dist[v]}\n"
    messagebox.showinfo("Алгоритм Дейкстри", text)


def run_floyd():
    D, prot = floyd_warshall()
    text = "\n".join(prot)

    text += "\n\nМатриця найкоротших шляхів:\n"
    header = "    " + " ".join(VERTICES) + "\n"
    text += header
    for i, v in enumerate(VERTICES):
        row = f"{v}: " + " ".join(str(D[i][j]) for j in range(len(VERTICES)))
        text += row + "\n"

    messagebox.showinfo("Алгоритм Флойда", text)


def run_graph_show():
    draw_graph()


# -------------------------------------------------------------
#                          GUI
# -------------------------------------------------------------

root = tk.Tk()
root.title("Лабораторна робота №3 — Алгоритми Дейкстри та Флойда")

algo_var = tk.StringVar(value="dijkstra")

tk.Label(root, text="Оберіть алгоритм:", font=("Arial", 14)).pack(pady=10)

tk.Radiobutton(root, text="Алгоритм Дейкстри", variable=algo_var,
               value="dijkstra").pack()
tk.Radiobutton(root, text="Алгоритм Флойда–Уоршелла", variable=algo_var,
               value="floyd").pack()

tk.Button(root, text="Виконати алгоритм", width=30,
          command=lambda: run_dijkstra() if algo_var.get() == "dijkstra" else run_floyd()
          ).pack(pady=10)

tk.Button(root, text="Показати граф", width=30, command=run_graph_show).pack(pady=10)

root.mainloop()
