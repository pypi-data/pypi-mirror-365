import datashader as ds
import datashader.transfer_functions as tf
from datashader.utils import export_image
from datashader.colors import colormap_select
from datashader.colors import inferno
from datashader.bundling import directly_connect_edges, hammer_bundle
import networkx as nx
import pandas as pd
import holoviews as hv


def visualize_graph(G, pos, output_path, width=800, height=600, cmap='inferno'):
        nodes_df = pd.DataFrame([(n, *pos[n]) for n in G.nodes()], columns=["id","x","y"])
        edges_df = pd.DataFrame([
            (u, v, pos[u][0], pos[u][1], pos[v][0], pos[v][1])
            for u, v in G.edges()
        ], columns=["source", "target", "x0", "y0", "x1", "y1"])
        edges_df["id"] = edges_df["source"].astype(str) + "_" + edges_df["target"].astype(str)
        edges_df = edges_df.set_index("id")
        nodes_df.set_index("id", inplace = True)
        
        r_nodes = hv.Points(nodes_df)
        r_edges = hv.Curve(edges_df)

        r_direct = hv.Curve(directly_connect_edges(r_nodes.data, r_edges.data), label="Direct")
        
        r_bundled = hv.Curve(hammer_bundle(r_nodes.data, r_edges.data, use_dask = True),label="Bundled")
        bundled_df = r_bundled.data
        bundled_df.reset_index(names = "edge_id", inplace = True)
        
        canvas = ds.Canvas(plot_width=600, plot_height=300, x_range=(0, 600), y_range=(0, 300))
        agg = canvas.line(bundled_df, 'x', 'y', agg = ds.count())
        
        # Step 5: Shade and export/view
        img = tf.dynspread(
            tf.shade(agg, cmap=inferno, how='eq_hist')
        )
        img = tf.set_background(img, None)
        pil_image = img.to_pil()

        
