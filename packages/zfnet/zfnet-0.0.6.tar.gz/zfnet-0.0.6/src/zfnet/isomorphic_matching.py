import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher
from networkx.drawing.layout import bipartite_layout
import pygmtools as pygm
from pygmtools.utils import build_aff_mat_from_networkx
import functools
import numpy as np
from scipy.optimize import linear_sum_assignment


def create_motifs():
    # Define example custom graphs to search for
    # 1. Feedforward network (simple chain)
    feedforward_graph = nx.DiGraph([(0, 1), (1, 2), (2, 3)])

    # 2. Diverging network
    diverging_graph = nx.DiGraph([(0, 1), (0, 2), (0, 3)])

    # 3. Converging network
    converging_graph = nx.DiGraph([(1, 0), (2, 0), (3, 0)])

    # 4. Feedback network
    feedback_graph = nx.DiGraph([(0, 1), (1, 2), (2, 0)])

    # 5. Recurrent network
    recurrent_graph = nx.DiGraph([(0, 1), (1, 2), (2, 3), (3, 0)])

    reciprocal_graph = nx.DiGraph([(0, 1), (1, 2)])

    # Custom graph list
    motifs = {
        "Feedforward": feedforward_graph,
        "Diverging": diverging_graph,
        "Converging": converging_graph,
        "Feedback": feedback_graph,
        "Recurrent": recurrent_graph,
        "Reciprocal": reciprocal_graph
    }
    return motifs

def nx_match_motifs(G, motif):
    matcher = DiGraphMatcher(G, motif)
    matches = list(matcher.subgraph_isomorphisms_iter())
    return matches


def pygm_match_motifs(G, motif):
    # Convert NetworkX graph to pygmtools format
    n1 = motif.number_of_nodes()
    n2 = G.number_of_nodes()
    gaussian_aff = functools.partial(pygm.utils.gaussian_aff_fn, sigma=.001) # set affinity function
    K = build_aff_mat_from_networkx(motif, G, edge_aff_fn = gaussian_aff)

    softmatch = pygm.rrwm(K, n1, n2)
    hardmatch = pygm.hungarian(softmatch)
    
    return hardmatch, softmatch

def get_matches_from_softmatch(match, G, threshold = 0.05):
    # get adjacency matrix of G
    A = nx.to_numpy_array(G, nodelist=G.nodes(), dtype=np.float32)
    root_idxs = np.where([match[0].flatten() > threshold])[1]

    matches = []
    # this doesnt work properly yet for every subgraph
    for root_idx in root_idxs:
        other_nodes = match[1:]
        outgoing = A[root_idx]
        incoming = A[:, root_idx].flatten()
        test = (outgoing * other_nodes)
        #test = (incoming * other_nodes)
        test = (outgoing * other_nodes) + (incoming * other_nodes)
        first_nodes, nodes = linear_sum_assignment(test, maximize = True)
        # check last node has incoming from second node

        # check 2nd node has incoming from first node
        
        # if any row ==0 - inproper match
        if (test[first_nodes, nodes]==0).any():
            pass
        else:
            motif_nodes = [root_idx, *nodes]

