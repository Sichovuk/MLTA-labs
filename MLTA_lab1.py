import tkinter as tk
from tkinter import messagebox, filedialog
import pprint
import networkx as nx
import matplotlib.pyplot as plt

# -----------------------------------------------------------
#          ДВА ГРАФИ (НЕОРІЄНТОВАНИЙ + ОРІЄНТОВАНИЙ)
# -----------------------------------------------------------

# НЕорієнтований граф
VERTICES_UNDIR = ['a', 'b', 'c', 'd', 'e', 'f']
EDGES_UNDIR = [
    ('a', 'b'),
    ('a', 'c'),
    ('b', 'd'),
    ('a', 'e'),
    ('b', 'e'),
    ('c', 'd'),
    ('c', 'd'),  # паралельне ребро
    ('c', 'f'),
    ('d', 'f'),
]

# Орієнтований граф
VERTICES_DIR = ['a', 'b', 'c', 'd', 'e', 'f']
EDGES_DIR = [
    ('a', 'b'),
    ('a', 'c'),
    ('a', 'e'),
    ('b', 'a'),
    ('b', 'c'),
    ('b', 'f'),
    ('e', 'a'),
    ('e', 'f'),
    ('e', 'd'),
    ('f', 'b'),
    ('f', 'd'),
]

# -----------------------------------------------------------
#                КООРДИНАТИ ДЛЯ ВІЗУАЛІЗАЦІЇ
# -----------------------------------------------------------

directed_positions = {
    'a': (-0.400,  0.500),
    'b': ( 0.400,  0.500),
    'c': ( 0.000,  0.100),
    'e': (-0.600, -0.500),
    'f': ( 0.600, -0.500),
    'd': ( 0.000, -0.700),
}

undirected_positions = {
    'a': (-0.400,  0.500),
    'b': ( 0.400,  0.500),
    'c': (-0.600, -0.500),
    'e': ( 0.000,  0.100),
    'd': ( 0.600, -0.500),
    'f': ( 0.000, -0.700),
}

# -----------------------------------------------------------
#                ПЕРЕТВОРЕННЯ ПРЕДСТАВЛЕНЬ
# -----------------------------------------------------------

def edges_to_adjacency_matrix(vertices, edges, directed=False):
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}
    A = [[0] * n for _ in range(n)]

    for u, v in edges:
        i, j = idx[u], idx[v]
        A[i][j] += 1
        if not directed:
            A[j][i] += 1
    return A


def edges_to_incidence_matrix(vertices, edges, directed=False):
    n, m = len(vertices), len(edges)
    idx = {v: i for i, v in enumerate(vertices)}
    Inc = [[0] * m for _ in range(n)]

    for col, (u, v) in enumerate(edges):
        i, j = idx[u], idx[v]
        if directed:
            Inc[i][col] = 1
            Inc[j][col] = -1
        else:
            Inc[i][col] = 1
            Inc[j][col] = 1
    return Inc


def adjacency_matrix_to_adj_list(vertices, A):
    n = len(vertices)
    adj = {v: [] for v in vertices}

    for i in range(n):
        for j in range(n):
            for _ in range(A[i][j]):
                adj[vertices[i]].append(vertices[j])
    return adj


# -----------------------------------------------------------
#             ВИБІР ПОТОЧНОГО ГРАФУ (directed/undirected)
# -----------------------------------------------------------

def get_graph_data():
    if graph_type_var.get() == "undirected":
        return VERTICES_UNDIR, EDGES_UNDIR, False, undirected_positions
    else:
        return VERTICES_DIR, EDGES_DIR, True, directed_positions


# -----------------------------------------------------------
#                GUI ФУНКЦІЇ ДЛЯ ВИВОДУ
# -----------------------------------------------------------

def show_adjacency_matrix():
    V, E, directed, _ = get_graph_data()
    A = edges_to_adjacency_matrix(V, E, directed)
    text = "\n".join(" ".join(str(x) for x in row) for row in A)
    messagebox.showinfo("Матриця суміжності", text)


def show_incidence_matrix():
    V, E, directed, _ = get_graph_data()
    Inc = edges_to_incidence_matrix(V, E, directed)
    text = "\n".join(" ".join(str(x) for x in row) for row in Inc)
    messagebox.showinfo("Матриця інцидентності", text)


def show_edge_list():
    _, E, _, _ = get_graph_data()
    text = "\n".join(f"{i+1}: {e}" for i, e in enumerate(E))
    messagebox.showinfo("Список ребер", text)


def show_adj_list():
    V, E, directed, _ = get_graph_data()
    A = edges_to_adjacency_matrix(V, E, directed)
    adj = adjacency_matrix_to_adj_list(V, A)
    text = pprint.pformat(adj)
    messagebox.showinfo("Список суміжності", text)


def draw_graph():
    V, E, directed, pos = get_graph_data()

    if directed:
        G = nx.DiGraph()
    else:
        G = nx.MultiGraph()

    G.add_nodes_from(V)
    G.add_edges_from(E)

    plt.figure(figsize=(7, 7))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color="lightblue" if directed else "orange",
        node_size=1300,
        font_size=14,
        arrows=directed,
        arrowstyle='-|>' if directed else '-',
        arrowsize=20,
    )

    plt.title("Орієнтований граф" if directed else "Неорієнтований граф")
    plt.show()


# -----------------------------------------------------------
#                    ЗБЕРЕЖЕННЯ У ФАЙЛ
# -----------------------------------------------------------

def save_adjacency():
    V, E, directed, _ = get_graph_data()
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file:
        return

    A = edges_to_adjacency_matrix(V, E, directed)
    with open(file, "w") as f:
        for row in A:
            f.write(" ".join(str(x) for x in row) + "\n")

    messagebox.showinfo("Успіх", "Матрицю суміжності збережено!")


def save_incidence():
    V, E, directed, _ = get_graph_data()
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file:
        return

    Inc = edges_to_incidence_matrix(V, E, directed)
    with open(file, "w") as f:
        for row in Inc:
            f.write(" ".join(str(x) for x in row) + "\n")

    messagebox.showinfo("Успіх", "Матрицю інцидентності збережено!")


def save_edge_list():
    _, E, _, _ = get_graph_data()
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file:
        return

    with open(file, "w") as f:
        for i, e in enumerate(E):
            f.write(f"{i+1}: {e}\n")

    messagebox.showinfo("Успіх", "Список ребер збережено!")


def save_adj_list():
    V, E, directed, _ = get_graph_data()
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file:
        return

    A = edges_to_adjacency_matrix(V, E, directed)
    adj = adjacency_matrix_to_adj_list(V, A)

    with open(file, "w", encoding="utf-8") as f:
        for v in adj:
            f.write(f"{v}: {adj[v]}\n")

    messagebox.showinfo("Успіх", "Список суміжності збережено!")


# -----------------------------------------------------------
#                           GUI
# -----------------------------------------------------------

root = tk.Tk()
root.title("Лабораторна робота №1 — Графи")

graph_type_var = tk.StringVar(value="undirected")

tk.Label(root, text="Оберіть тип графа:", font=("Arial", 14)).pack(pady=10)

tk.Radiobutton(root, text="Неорієнтований граф", variable=graph_type_var, value="undirected").pack()
tk.Radiobutton(root, text="Орієнтований граф", variable=graph_type_var, value="directed").pack()

tk.Label(root, text="Виберіть дію:", font=("Arial", 14)).pack(pady=10)

tk.Button(root, text="Показати матрицю суміжності", width=35, command=show_adjacency_matrix).pack(pady=5)
tk.Button(root, text="Показати матрицю інцидентності", width=35, command=show_incidence_matrix).pack(pady=5)
tk.Button(root, text="Показати список ребер", width=35, command=show_edge_list).pack(pady=5)
tk.Button(root, text="Показати список суміжності", width=35, command=show_adj_list).pack(pady=5)
tk.Button(root, text="Показати граф (візуально)", width=35, command=draw_graph).pack(pady=10)

tk.Label(root, text="Зберегти у файл:", font=("Arial", 14)).pack(pady=10)

tk.Button(root, text="Зберегти матрицю суміжності", width=35, command=save_adjacency).pack(pady=5)
tk.Button(root, text="Зберегти матрицю інцидентності", width=35, command=save_incidence).pack(pady=5)
tk.Button(root, text="Зберегти список ребер", width=35, command=save_edge_list).pack(pady=5)
tk.Button(root, text="Зберегти список суміжності", width=35, command=save_adj_list).pack(pady=5)

root.mainloop()
