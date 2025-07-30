from networkx.algorithms.graph_hashing import weisfeiler_lehman_graph_hash # type:ignore
from core.utils import ast_to_nx

class CodePatternMatcher:
    def __init__(self):
        self.pattern_hashes = {}  # pattern_name -> hash

    def hash_ast(self, cursor):
        G = ast_to_nx(cursor)
        return weisfeiler_lehman_graph_hash(G, node_attr='label')
