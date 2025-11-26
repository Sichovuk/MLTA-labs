import tkinter as tk
from tkinter import messagebox, filedialog
import pprint
import networkx as nx
import matplotlib.pyplot as plt

# ------------------ ГРАФ З РИСУНКА ------------------

DIRECTED = False

VERTICES = ['a', 'b', 'c', 'd', 'e', 'f']

EDGES = [
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

# ------------------ ПЕРЕТВОРЕННЯ ------------------

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


# ------------------ ФУНКЦІЇ ДЛЯ GUI ------------------

def show_adjacency_matrix():
    A = edges_to_adjacency_matrix(VERTICES, EDGES)
    text = "\n".join(" ".join(str(x) for x in row) for row in A)
    messagebox.showinfo("Матриця суміжності", text)


def show_incidence_matrix():
    Inc = edges_to_incidence_matrix(VERTICES, EDGES)
    text = "\n".join(" ".join(str(x) for x in row) for row in Inc)
    messagebox.showinfo("Матриця інцидентності", text)


def show_edge_list():
    text = "\n".join(f"{i+1}: {e}" for i, e in enumerate(EDGES))
    messagebox.showinfo("Список ребер", text)


def show_adj_list():
    A = edges_to_adjacency_matrix(VERTICES, EDGES)
    adj = adjacency_matrix_to_adj_list(VERTICES, A)
    text = pprint.pformat(adj)
    messagebox.showinfo("Список суміжності", text)


def draw_graph():
    G = nx.MultiGraph()  # щоб підтримувати паралельні ребра
    G.add_nodes_from(VERTICES)
    G.add_edges_from(EDGES)

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(6, 6))
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=1200, font_size=14)
    plt.title("Граф зі світлини")
    plt.show()


# ------------------ ЗБЕРЕЖЕННЯ ------------------

def save_adjacency():
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file:
        return

    A = edges_to_adjacency_matrix(VERTICES, EDGES)
    with open(file, "w") as f:
        for row in A:
            f.write(" ".join(str(x) for x in row) + "\n")

    messagebox.showinfo("Успіх", "Матрицю суміжності збережено!")


def save_incidence():
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file:
        return

    Inc = edges_to_incidence_matrix(VERTICES, EDGES)
    with open(file, "w") as f:
        for row in Inc:
            f.write(" ".join(str(x) for x in row) + "\n")

    messagebox.showinfo("Успіх", "Матрицю інцидентності збережено!")


def save_edge_list():
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file:
        return

    with open(file, "w") as f:
        for i, e in enumerate(EDGES):
            f.write(f"{i+1}: {e}\n")

    messagebox.showinfo("Успіх", "Список ребер збережено!")


def save_adj_list():
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file:
        return

    A = edges_to_adjacency_matrix(VERTICES, EDGES)
    adj = adjacency_matrix_to_adj_list(VERTICES, A)

    with open(file, "w", encoding="utf-8") as f:
        for v in adj:
            f.write(f"{v}: {adj[v]}\n")

    messagebox.showinfo("Успіх", "Список суміжності збережено!")


# ------------------ GUI ------------------

root = tk.Tk()
root.title("Лабораторна робота №1 — Графи")

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
