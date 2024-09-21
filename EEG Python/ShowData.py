import os
import sys
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable 
from networkx.algorithms.community import greedy_modularity_communities
import numpy as np
from scipy.stats import pearsonr
import traceback
from tkinter import ttk


if len(sys.argv) < 4:
    print("Error: Missing required arguments")
    sys.exit(1)
selected_analysis_type = sys.argv[1]  # 'ADHD' or 'NonADHD'
selected_threshold = float(sys.argv[2])
selected_patient = sys.argv[3] 

def get_segment_count(main_folder_path):
    target_folder_name = f"{selected_analysis_type}_{selected_patient}"
    count = 0
    try:
        folders = [f for f in os.listdir(main_folder_path) if os.path.isdir(os.path.join(main_folder_path, f))]
        relevant_folder = next((folder for folder in folders if target_folder_name in folder), None)
        if relevant_folder is None:
            print(f"No folder found for {target_folder_name}")
            return 0

        relevant_folder_path = os.path.join(main_folder_path, relevant_folder)
        for filename in os.listdir(relevant_folder_path):
            if os.path.isfile(os.path.join(relevant_folder_path, filename)):
                count += 1
    except Exception as e:
        print(f"An error occurred while searching or counting: {e}")
        return 0

    return count // 2

def process_segment(file_path, master, selected_threshold):
    try:
        matrix = load_connectivity_matrix(file_path)
        thresholded_matrix = apply_threshold(matrix, selected_threshold)
        G = build_graph(thresholded_matrix)
        plot_graph(G, master)
    except Exception as e:
        print(f"An error occurred while trying to process the segment: {e}")

def build_community_detection(file_path, master, selected_threshold):
    try:
        matrix = load_connectivity_matrix(file_path)
        thresholded_matrix = apply_threshold(matrix, selected_threshold)
        G = build_graph_com(thresholded_matrix)
        communities = list(greedy_modularity_communities(G))
        plot_communities(G, communities, master)
    except Exception as e:
        print("An error occurred during community detection:")
        print(f"Error type: {type(e).__name__}, Error message: {e}")
        traceback.print_exc()  # This will print the full traceback, providing detailed error information
def plot_communities(G, communities, master):
    plt.close('all')
    fig, ax = plt.subplots(figsize=(5, 5)) 
   
    pos = {node: positions_10_20[node] for node in G.nodes()}

    # Draw communities with different colors
    colors = plt.cm.tab10.colors  
    for i, community in enumerate(communities):
        community_nodes = [node for node in community if node in pos]
        nx.draw_networkx_nodes(G, pos, nodelist=community_nodes, node_color=[colors[i % len(colors)]], node_size=500, ax=ax)

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.5)

    # Draw labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10)

    # Remove the axes
    ax.set_axis_off()

    # Hide the spines, ticks, and labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Embed the plot into the Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.place(relx=0.7, rely=0.5, anchor='center')



import networkx as nx

def build_graph_measures(file_path, master, selected_threshold):
    try:
        matrix = load_connectivity_matrix(file_path)
        thresholded_matrix = apply_threshold(matrix, selected_threshold)
        G = build_graph(thresholded_matrix)

        average_degree = np.mean([d for n, d in G.degree()]) if G else 0
        print(average_degree)
        global_efficiency = calculate_global_efficiency(G) 
        print(global_efficiency)
        clustering_coeff = nx.average_clustering(G) if G else 0
        print(clustering_coeff)
        shortest_path_length = calculate_average_shortest_path_length_p(G)if G else 0
        modularity= calculate_modularity(G)
        measures = {
            'Clustering Coefficient': clustering_coeff,
            'Average Shortest Path Length': shortest_path_length,
            'Average Degree (Global)': average_degree,
            'Global Efficiency': global_efficiency,
            'Modularity': modularity,
        }

        # Display the measures in the GUI
        
        display_graph_measures(measures, master)

    except Exception as e:
        print(f"An error occurred during graph measures calculation: {e}")

def calculate_modularity(G):
    try:
        # Fixing negative weights by taking their absolute value
        for u, v, d in G.edges(data=True):
            d['weight'] = abs(d['weight'])  
        
        # Step 1: Detect communities
        communities = list(greedy_modularity_communities(G))
        
        # Step 2: Calculate modularity
        modularity = nx.community.modularity(G, communities)
        
        # Step 3: Check for out-of-range modularity values
        if modularity < -1 or modularity > 1:
            print(f"Warning: Modularity value {modularity} is out of the expected range [-1, 1].")
            modularity = max(min(modularity, 1), -1)
        
        return modularity
    
    except Exception as e:
        print(f"An error occurred during the modularity calculation: {e}")
        return None



def display_graph_measures(measures, master):
    for widget in master.winfo_children():
        if widget.winfo_name().startswith('measures_frame'):
            widget.destroy()

    # Create a frame to hold the plot
    measures_frame = tk.Frame(master, name='measures_frame')
    measures_frame.place(relx=0.5, rely=0.5, anchor='center')

    # Create a figure for plotting
    fig, ax = plt.subplots(figsize=(6, 4))  
    measure_names = list(measures.keys())
    measure_values = list(measures.values())

    # Creating the bar chart with a purple color
    bars = ax.bar(measure_names, measure_values, color='purple')
    ax.set_title('Graph Measures')
    ax.set_ylabel('Value')
    ax.set_xticklabels(measure_names, rotation=45, ha='right')
    ax.set_ylim(0, max(measure_values) * 1.2)  

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval * 1.01,  
                f'{yval:.2f}',  
                va='bottom', 
                ha='center', 
                color='black', fontsize=8)

    plt.tight_layout()

    # Embed the plot into the Tkinter frame
    canvas = FigureCanvasTkAgg(fig, master=measures_frame)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)


def load_connectivity_matrix(file_path):
    return pd.read_csv(file_path, header=None, skiprows=1) 

def apply_threshold(matrix, threshold):
    significant_connections = np.abs(matrix) > threshold
    return np.where(significant_connections, matrix, 0)


# 10-20 system positions for plotting
positions_10_20 = {
    'Fp1': (-0.5, 1), 'Fp2': (0.5, 1),
    'F3': (-0.6, 0.5), 'F4': (0.6, 0.5),
    'C3': (-0.7, 0), 'C4': (0.7, 0),
    'P3': (-0.6, -0.5), 'P4': (0.6, -0.5),
    'O1': (-0.5, -1), 'O2': (0.5, -1),
    'F7': (-1, 0.5), 'F8': (1, 0.5),
    'T7': (-1, 0), 'T8': (1, 0),
    'P7': (-1, -0.5), 'P8': (1, -0.5),
    'Fz': (0, 0.75), 'Cz': (0, 0), 'Pz': (0, -0.75)
    }


def build_graph(matrix):
    G = nx.Graph()
    n = matrix.shape[0]  # Number of rows
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n): 
            if matrix[i, j] != 0:
                G.add_edge(i, j, weight=matrix[i, j])
    return G



def build_graph_com(matrix):
    G = nx.Graph()
    n = matrix.shape[0]  
    labels = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T7', 'T8', 'P7', 'P8', 'Fz', 'Cz', 'Pz']
    
    
    G.add_nodes_from(labels[:n])  

    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i, j] != 0:
                G.add_edge(labels[i], labels[j], weight=matrix[i, j])
    return G

def plot_graph(G, master):
    plt.close('all')
    fig, ax = plt.subplots(figsize=(5, 5))  
    
    # Using the defined 10-20 positions for electrodes
    pos = {i: positions_10_20[label] for i, label in enumerate(positions_10_20)}
    
    labels = {i: label for i, label in enumerate(positions_10_20)}

    nx.draw(G, pos, ax=ax, labels=labels, with_labels=True, node_color='#D3BFFF', node_size=500, edge_color='#800080', width=2)

    # Draw the plot on the Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.place(relx=0.7, rely=0.5, anchor='center')

def calculate_average_shortest_path_length_p(G):
    """
    Calculate the average shortest path length for a graph G. If the graph is connected,
    use the built-in function. If not, calculate the average for each component and then average those,
    weighted by the number of pairs in each component, and including a fixed distance for disconnected pairs.
    
    :param G: NetworkX graph
    :return: Weighted average of shortest path lengths or direct average if the graph is connected
    """
    if nx.is_connected(G):
        # Use built-in function if the graph is fully connected
        return nx.average_shortest_path_length(G)
    else:
        lengths = []
        components = list(nx.connected_components(G))
        num_nodes = G.number_of_nodes()
        
        # Calculate the number of pairs in each component
        component_pairs = [(len(c) * (len(c) - 1) / 2) for c in components]
        
        # Calculate the average shortest path length for each component
        for component, pairs in zip(components, component_pairs):
            subgraph = G.subgraph(component)
            if pairs > 0:
                lengths.append(nx.average_shortest_path_length(subgraph) * pairs)
        
        # Sum of distances for reachable pairs
        total_length = sum(lengths)
        
        # Handle unreachable pairs
        total_pairs = num_nodes * (num_nodes - 1) / 2
        reachable_pairs = sum(component_pairs)
        unreachable_pairs = total_pairs - reachable_pairs
        max_dist = 19  # Assigning 19 as the distance for unreachable pairs
        total_length += max_dist * unreachable_pairs
        
        return total_length / total_pairs

import networkx as nx

def calculate_global_efficiency(G):
    """
    Calculate the global efficiency of a graph G, excluding disconnected pairs.
    
    Parameters:
    G : NetworkX graph
        The graph for which to calculate global efficiency.
    
    Returns:
    global_efficiency : float
        The global efficiency of the graph.
    """
    n = len(G)
    if n < 2:
        return 0  # A graph with fewer than 2 nodes has no global efficiency.
    
    efficiency_sum = 0
    connected_pairs_count = 0
    
    # Iterate over all pairs of nodes in the graph
    for node1 in G.nodes:
        for node2 in G.nodes:
            if node1 != node2:
                try:
                    # Compute the shortest path between node1 and node2
                    distance = nx.shortest_path_length(G, source=node1, target=node2)
                    efficiency_sum += 1 / distance
                    connected_pairs_count += 1  # Count the connected pair
                except nx.NetworkXNoPath:
                    # Skip disconnected pairs (do not count them in efficiency calculation)
                    continue
    
    if connected_pairs_count == 0:
        return 0  # Avoid division by zero if no connected pairs
    
    global_efficiency = efficiency_sum / connected_pairs_count
    return global_efficiency