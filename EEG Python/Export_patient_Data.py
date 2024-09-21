import os
import sys
import pandas as pd
import numpy as np
import networkx as nx
import glob
from tkinter import messagebox
from ShowData import get_segment_count, load_connectivity_matrix, apply_threshold, build_graph, calculate_modularity
from networkx.algorithms.community import greedy_modularity_communities
# Variables setup
selected_analysis_type = sys.argv[1]  # 'ADHD' or 'NonADHD'
selected_threshold = float(sys.argv[2])
selected_patient = sys.argv[3] 
base_input_directory = r'C:\EEG Python'



def clac_all_psegment_measures(analysis_type, patient, selected_threshold):
    full_folder_path = "C:\\EEG Python\\creatdata"
    input_directory = base_input_directory
    if analysis_type == 'ADHD':
        input_directory = os.path.join(base_input_directory, 'ADHDexcel')
    elif analysis_type == 'NonADHD':
        input_directory = os.path.join(base_input_directory, 'NonADHDexcel')
    else:
        print(f"Error: Unexpected analysis type '{analysis_type}'. Defaulting to base input directory.")
    
    file_name = f"{patient}_analysis.csv"
    file_path = os.path.join(input_directory, file_name)
    
    # Overwrite the file if it exists
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}. Overwriting the file.")
    
    # Create a new file with headers
    df = pd.DataFrame(columns=['Segment_number', 'Average Degree (Global)', 'Global Efficiency', 'Average Shortest Path Length', 'Clustering Coefficient','Modularity'])
    df.to_csv(file_path, index=False)
    print(f"Created or overwritten file: {file_path}")

    segment_count = get_segment_count(full_folder_path)
    target_folder_pattern = f"{analysis_type}_{patient}*"
    base_folder_path = os.path.join(full_folder_path, target_folder_pattern)
    matching_folders = glob.glob(base_folder_path)
    
    if not matching_folders:
        print(f"No folder found for {analysis_type}_{patient}")
        return
    
    full_folder_path = matching_folders[0]
    for i in range(1, segment_count + 1):
        pattern = f"segment_{i}_{patient}*_*_connectivity.csv"
        matching_files = glob.glob(os.path.join(full_folder_path, pattern))
        if matching_files:
            segment_file_path = matching_files[0]
            measures_to_excel1(file_path, segment_file_path, i, selected_threshold)
        else:
            print(f"No file found for graph measures on segment {i}")
    
    # Calculate averages and append to the CSV file
    df = pd.read_csv(file_path)
    average_degree_mean = df['Average Degree (Global)'].mean()
    global_efficiency_mean = df['Global Efficiency'].mean()
    shortest_path_length_mean = df['Average Shortest Path Length'].mean()
    clustering_coefficient_mean = df['Clustering Coefficient'].mean()
    modularity_mean= df['Modularity'].mean()

    averages_row = pd.DataFrame({
        'Segment_number': ['Average'],
        'Average Degree (Global)': [average_degree_mean],
        'Global Efficiency': [global_efficiency_mean],
        'Average Shortest Path Length': [shortest_path_length_mean],
        'Clustering Coefficient': [clustering_coefficient_mean],
        'Modularity':[modularity_mean]
    })

    df = pd.concat([df, averages_row], ignore_index=True)
    df.to_csv(file_path, index=False)
    messagebox.showinfo("Success", "Data has been exported and averages calculated successfully.")


    # Show success message
    #messagebox.showinfo("Success", "Data has been exported and averages calculated successfully.")


def measures_to_excel1(results_file_path, segment_file_path, segment_number, selected_threshold):
    try:
        matrix = load_connectivity_matrix(segment_file_path)
        print(f"Loaded matrix for segment {segment_number}:")
       

        thresholded_matrix = apply_threshold(matrix, float(selected_threshold))
        print(f"Thresholded matrix for segment {segment_number}:")
     

        G = build_graph(thresholded_matrix)
        print(f"Graph info for segment {segment_number}: Nodes - {len(G.nodes)}, Edges - {len(G.edges)}")

        average_degree = np.mean([d for n, d in G.degree()]) if G else 0
        print(average_degree)
        global_efficiency = calculate_global_efficiency(G) 
        print(global_efficiency)
        clustering_coeff = nx.average_clustering(G) if G else 0
        print(clustering_coeff)
        shortest_path_length = calculate_average_shortest_path_length(G)if G else 0
        modularity= calculate_modularity(G)
        new_row = pd.DataFrame({
            'Segment_number': [segment_number],
            'Average Degree (Global)': [average_degree],
            'Global Efficiency': [global_efficiency],
            'Average Shortest Path Length': [shortest_path_length],
            'Clustering Coefficient': [clustering_coeff],
            'Modularity':[modularity]
        })

        with open(results_file_path, 'a') as f:
            new_row.to_csv(f, index=False, header=False)

    except Exception as e:
        print(f"An error occurred during graph measures calculation for segment {segment_number}: {e}")



def calculate_average_shortest_path_length(G):
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
    
    # Normalize the global efficiency by the number of connected node pairs
    global_efficiency = efficiency_sum / connected_pairs_count
    return global_efficiency