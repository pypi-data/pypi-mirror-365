import networkx as nx # type:ignore
from clang.cindex import Cursor # type:ignore
from graphviz import Digraph # type:ignore
import json

# Convert AST to NetworkX graph
def ast_to_nx(cursor: Cursor):
    G = nx.DiGraph()
    node_counter = [0]
    def add_node(cur, parent_id=None):
        node_counter[0] += 1
        node_id = node_counter[0]
        label = ''.join([w.capitalize() for w in cur.kind.name.lower().split('_')])
        spelling = cur.spelling or ""
        G.add_node(node_id, kind=label, spelling=spelling, label=f"{label}\n'{spelling}'" if spelling else label)
        if parent_id is not None:
            G.add_edge(parent_id, node_id)
        for child in cur.get_children():
            add_node(child, node_id)
        return node_id
    add_node(cursor)
    return G

# Print the AST as a tree in the terminal
def print_ast(cursor, indent="", is_last=True):
    branch = "└── " if is_last else "├── "
    label = ''.join([w.capitalize() for w in cursor.kind.name.lower().split('_')])
    if cursor.spelling:
        label += f" '{cursor.spelling}'"
    print(indent + branch + label)
    children = list(cursor.get_children())
    for i, child in enumerate(children):
        is_child_last = (i == len(children) - 1)
        print_ast(child, indent + ("    " if is_last else "│   "), is_child_last)

# Visualize AST using Graphviz
def visualize_ast_graphviz(cursor, dot=None, parent_id=None, node_counter=[0]):
    if dot is None:
        dot = Digraph(comment="C++ AST", format="png")
        dot.attr(rankdir="TB", size="8,10")
    node_counter[0] += 1
    node_id = f"n{node_counter[0]}"
    label = ''.join([w.capitalize() for w in cursor.kind.name.lower().split('_')])
    if cursor.spelling:
        label += f"\n'{cursor.spelling}'"
    dot.node(node_id, label, shape="box", style="filled", fillcolor="#e6f2ff", fontname="monospace")
    if parent_id is not None:
        dot.edge(parent_id, node_id)
    for child in cursor.get_children():
        visualize_ast_graphviz(child, dot, node_id, node_counter)
    return dot

# Convert AST to JSON format
def ast_to_json(cursor: Cursor):
    def node_to_dict(cur):
        d = {
            "kind": ''.join([w.capitalize() for w in cur.kind.name.lower().split('_')]),
            "spelling": cur.spelling,
            "children": [node_to_dict(child) for child in cur.get_children()]
        }
        return d
    return json.dumps(node_to_dict(cursor), indent=2)
