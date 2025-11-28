import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

# -----------------------------------------------------------
#                 ДВА ГРАФИ: ОРІЄНТОВАНИЙ І НЕОРІЄНТОВАНИЙ
# -----------------------------------------------------------

# Орієнтований граф (Граф ЛР №2)
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

# Неорієнтований граф (Граф ЛР №1)
VERTICES_UNDIR = ['a', 'b', 'c', 'd', 'e', 'f']
EDGES_UNDIR = [
    ('a', 'b'),
    ('a', 'c'),
    ('b', 'd'),
    ('a', 'e'),
    ('b', 'e'),
    ('c', 'd'),
    ('c', 'd'),
    ('c', 'f'),
    ('d', 'f'),
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
#                   ДОПОМІЖНІ СТРУКТУРИ
# -----------------------------------------------------------

def build_adj_list(vertices, edges, directed=False):
    adj = {v: [] for v in vertices}
    for u, v in edges:
        adj[u].append(v)
        if not directed:
            adj[v].append(u)
    for v in adj:
        adj[v].sort()
    return adj


# -----------------------------------------------------------
#                       DFS ПРОТОКОЛ
# -----------------------------------------------------------

def dfs_protocol(vertices, edges, start, directed=False):
    adj = build_adj_list(vertices, edges, directed)
    visited = set()
    dfs_num = {}
    stack = []
    protocol = []
    counter = 1

    stack.append(start)
    dfs_num[start] = counter
    protocol.append((start, counter, stack.copy()))
    visited.add(start)

    while stack:
        x = stack[-1]

        found = False
        for y in adj[x]:
            if y not in visited:
                counter += 1
                dfs_num[y] = counter
                stack.append(y)
                visited.add(y)
                protocol.append((y, counter, stack.copy()))
                found = True
                break

        if not found:
            stack.pop()
            if stack:
                protocol.append((x, "-", stack.copy()))

    return protocol


# -----------------------------------------------------------
#                       BFS ПРОТОКОЛ
# -----------------------------------------------------------

def bfs_protocol(vertices, edges, start, directed=False):
    adj = build_adj_list(vertices, edges, directed)
    visited = set()
    bfs_num = {}
    protocol = []
    queue = deque()
    counter = 1

    queue.append(start)
    bfs_num[start] = counter
    visited.add(start)
    protocol.append((start, counter, list(queue)))

    while queue:
        x = queue[0]

        for y in adj[x]:
            if y not in visited:
                counter += 1
                bfs_num[y] = counter
                visited.add(y)
                queue.append(y)
                protocol.append((y, counter, list(queue)))

        queue.popleft()
        if queue:
            protocol.append((x, "-", list(queue)))

    return protocol


# -----------------------------------------------------------
#                ВІЗУАЛІЗАЦІЯ ГРАФУ (З КООРДИНАТАМИ)
# -----------------------------------------------------------

def draw_graph(vertices, edges, directed=False):
    if directed:
        G = nx.DiGraph()
        pos = directed_positions
    else:
        G = nx.MultiGraph()
        pos = undirected_positions

    G.add_nodes_from(vertices)
    G.add_edges_from(edges)

    plt.figure(figsize=(7, 7))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color="lightblue" if directed else "orange",
        node_size=1200,
        font_size=14,
        arrows=directed,
        arrowstyle='-|>' if directed else '-',
        arrowsize=20,
    )

    plt.title("Орієнтований граф" if directed else "Неорієнтований граф")
    plt.show()


# -----------------------------------------------------------
#                     GUI ІНТЕРФЕЙС
# -----------------------------------------------------------

root = tk.Tk()
root.title("Лабораторна робота №2 — DFS/BFS двох графів")

graph_type_var = tk.StringVar(value="directed")


def run_dfs():
    gtype = graph_type_var.get()

    if gtype == "directed":
        prot = dfs_protocol(VERTICES_DIR, EDGES_DIR, 'a', directed=True)
    else:
        prot = dfs_protocol(VERTICES_UNDIR, EDGES_UNDIR, 'a', directed=False)

    text = "\n".join(str(row) for row in prot)
    messagebox.showinfo("DFS-протокол", text)


def run_bfs():
    gtype = graph_type_var.get()

    if gtype == "directed":
        prot = bfs_protocol(VERTICES_DIR, EDGES_DIR, 'a', directed=True)
    else:
        prot = bfs_protocol(VERTICES_UNDIR, EDGES_UNDIR, 'a', directed=False)

    text = "\n".join(str(row) for row in prot)
    messagebox.showinfo("BFS-протокол", text)


def show_graph():
    gtype = graph_type_var.get()
    if gtype == "directed":
        draw_graph(VERTICES_DIR, EDGES_DIR, directed=True)
    else:
        draw_graph(VERTICES_UNDIR, EDGES_UNDIR, directed=False)


# -----------------------------------------------------------
#                   КОМПОНЕНТИ ІНТЕРФЕЙСУ
# -----------------------------------------------------------

tk.Label(root, text="Оберіть граф:", font=("Arial", 14)).pack(pady=10)

tk.Radiobutton(root, text="Орієнтований граф",
               variable=graph_type_var, value="directed").pack()

tk.Radiobutton(root, text="Неорієнтований граф",
               variable=graph_type_var, value="undirected").pack()

tk.Label(root, text="Оберіть дію:", font=("Arial", 14)).pack(pady=10)

tk.Button(root, text="Виконати DFS", width=30, command=run_dfs).pack(pady=5)
tk.Button(root, text="Виконати BFS", width=30, command=run_bfs).pack(pady=5)
tk.Button(root, text="Показати граф", width=30, command=show_graph).pack(pady=10)

root.mainloop()
