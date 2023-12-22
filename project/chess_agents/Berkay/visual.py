from graphviz import Digraph

def visualize_tree(node, graph=None):
    if graph is None:
        graph = Digraph()

    # Add the current node to the graph
    node_label = f"\nScore: {node.score}\nVisits: {node.times_visited}"
    graph.node(str(id(node)), label=node_label)

    for child in node.children.values():
        # Add the child node to the graph
        graph.node(str(id(child)), label=f"Move:...")

        # Connect the current node to the child
        graph.edge(str(id(node)), str(id(child)))

        # Recursive call for the child
        visualize_tree(child, graph)

    return graph
