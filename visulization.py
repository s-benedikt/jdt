import networkx as nx
import matplotlib.pyplot as plt

def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0., xcenter=0.5):
    """
    From Joel's answer on StackOverflow for tree layout in networkx
    """
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G))) 
        else:
            import random
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0., xcenter=0.5, pos=None, parent=None):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                     vert_loc=vert_loc-vert_gap, xcenter=nextx,
                                     pos=pos, parent=root)
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

G = nx.DiGraph()
nodes = [
    (0, "Schema\n(root_type=object,\nclosed=False)"),
    (1, "Properties"),
    (2, "Property:\n'Name'"),
    (3, "Constraint: and"),
    (4, "Constraint:\nstring"),
    (5, "Constraint:\nrequired"),
    (6, "Property:\n'Age'"),
    (7, "Constraint: and"),
    (8, "Constraint:\nnumber"),
    (9, "Constraint:\nrequired"),
    (10, "Property:\n'Student'\n[container]"),
    (11, "Property:\n'StudentID'"),
    (12, "Constraint: and"),
    (13, "Constraint:\nnumber"),
    (14, "Constraint:\nrequired"),
    (15, "Property:\n'Major'"),
    (16, "Constraint: and"),
    (17, "Constraint:\nstring"),
    (18, "Constraint:\nrequired"),
    (19, "Property:\n'Level'"),
    (20, "Constraint: and"),
    (21, "Constraint:\nstring"),
    (22, "Constraint:\nrequired")
]
edges = [
    (0,1),
    (1,2), (1,6), (1,10),
    (2,3), (3,4), (3,5),
    (6,7), (7,8), (7,9),
    (10,11), (10,15), (10,19),
    (11,12), (12,13), (12,14),
    (15,16), (16,17), (16,18),
    (19,20), (20,21), (20,22)
]

for node_id, label in nodes:
    G.add_node(node_id, label=label)
G.add_edges_from(edges)

pos = hierarchy_pos(G, 0, width=2.0)
fig, ax = plt.subplots(figsize=(18, 10))

labels = nx.get_node_attributes(G, 'label')

colors = []
for node in G.nodes():
    label = labels[node]
    if "Schema" in label: colors.append('#aec7e8')
    elif "Properties" in label: colors.append('#c7c7c7')
    elif "Property:" in label: colors.append('#98df8a')
    elif "Constraint: and" in label: colors.append('#ffbb78')
    else: colors.append('#ff9896')

# Draw edges
nx.draw_networkx_edges(G, pos, ax=ax, arrows=True, arrowsize=15, edge_color='gray')

# Draw nodes as bounding boxes with text
for node, (x, y) in pos.items():
    ax.text(x, y, labels[node], size=10, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors[node], edgecolor="black", alpha=0.9))

plt.margins(0.1)
plt.axis('off')
plt.title("AST Visualization", fontsize=18, pad=20)
plt.savefig('ast_visualization.png', bbox_inches='tight', dpi=150)
plt.close()
print("Success")