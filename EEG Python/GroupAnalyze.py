import os
import glob
import pandas as pd
import numpy as np
import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import createData
from tkinter import messagebox
import numpy as np
from scipy.stats import pearsonr
from networkx.algorithms.community import greedy_modularity_communities


base_input_directory = r'C:\EEG Python'


def data_group_func(selected_threshold, progress_callback=None):
    total_patients = 121 
    processed = 0

    # Processing ADHD patients
    for i in range(1, 62):
        createData.main("ADHD", f"patient {i}")
        clac_all_psegment_measures1("ADHD", f"patient {i}", selected_threshold)
        processed += 1
        if progress_callback:
            progress_callback(int((processed / total_patients) * 100))

    # Processing NonADHD patients
    for i in range(1, 61): 
        createData.main("NonADHD", f"patient {i}")
        clac_all_psegment_measures1("NonADHD", f"patient {i}", selected_threshold)
        processed += 1
        if progress_callback:
            progress_callback(int((processed / total_patients) * 100))

    Adhd_path = os.path.join(base_input_directory, 'ADHDexcel')
    NonAdhd_path = os.path.join(base_input_directory, 'NonADHDexcel')

    adhd_averages = calc_avg(Adhd_path, "ADHD")
    nonadhd_averages = calc_avg(NonAdhd_path, "NonADHD")

    # Final call to progress callback to ensure completion is reported
    if progress_callback:
        progress_callback(100)

    print(adhd_averages)
    print(nonadhd_averages)
    return adhd_averages, nonadhd_averages

def calc_avg(folder_path, data_type):
    all_files = glob.glob(os.path.join(folder_path, "*.csv"))
    sum_avg_degree = 0
    sum_global_efficiency = 0
    sum_avg_shortest_path = 0
    sum_clustering_coeff = 0
    sum_modularity= 0
    
    # Summing values from each file
    for file in all_files:
        df = pd.read_csv(file)
        print(file)
        sum_avg_degree += df['Average Degree (Global)'].iloc[-1]
        print(sum_avg_degree)
        sum_global_efficiency += df['Global Efficiency'].iloc[-1]
        sum_avg_shortest_path += df['Average Shortest Path Length'].iloc[-1]
        sum_clustering_coeff += df['Clustering Coefficient'].iloc[-1]
        sum_modularity+= df['Modularity'].iloc[-1]
   
    if data_type == 'ADHD':
        divisor = 61  # The number of the patietns in the ADHD group
    elif data_type == 'NonADHD':
        divisor = 60 # The number of the patietns in the Non-ADHD group
    else:
        raise ValueError("Invalid data type specified. Choose 'ADHD' or 'NonADHD'.")

    # Calculating the average by dividing the sum by the divisor
    avg_degree_mean = sum_avg_degree / divisor
    global_efficiency_mean = sum_global_efficiency / divisor
    avg_shortest_path_mean = sum_avg_shortest_path / divisor
    clustering_coeff_mean = sum_clustering_coeff / divisor
    modularity_mean = sum_modularity/divisor
    
    return [avg_degree_mean, global_efficiency_mean, avg_shortest_path_mean, clustering_coeff_mean, modularity_mean]




def plot(adhd_averages, nonadhd_averages, frame):
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    
    measures = ['Average Degree', 'Global Efficiency', 'Average Shortest Path Length', 'Clustering Coefficient', 'Modularity']
    x = np.arange(len(measures))
    width = 0.35  # Bar width    
    fig, ax = plt.subplots(figsize=(10, 6))
    soft_blue = '#6495ED'  
    purple = 'purple'

    # Plot all values on the same y-axis for simplicity
    ax.bar(x - width/2, adhd_averages, width, label='ADHD', color=soft_blue, alpha=0.7)
    ax.bar(x + width/2, nonadhd_averages, width, label='NonADHD', color=purple, alpha=0.7)
    ax.set_ylabel('Average Values')
    ax.set_ylim(0, max(max(adhd_averages), max(nonadhd_averages)) * 1.2) 

    # Set x-axis labels
    ax.set_xticks(x)
    ax.set_xticklabels(measures, rotation=25, ha='right')

    # Title and labels
    ax.set_xlabel('Measures')
    ax.set_title('Comparison of Graph Measures for ADHD and NonADHD')

    ax.legend(loc='upper right')

    for i in range(len(adhd_averages)):
        ax.text(x[i] - width/2, adhd_averages[i], f'{adhd_averages[i]:.2f}', ha='center', va='bottom', fontsize=8)
        ax.text(x[i] + width/2, nonadhd_averages[i], f'{nonadhd_averages[i]:.2f}', ha='center', va='bottom', fontsize=8)

    
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)




def clac_all_psegment_measures1(analysis_type, patient, selected_threshold):
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

    segment_count = get_segment_count1(full_folder_path,analysis_type, patient)
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
    modularity_meam= df['Modularity'].mean()

    averages_row = pd.DataFrame({
        'Segment_number': ['Average'],
        'Average Degree (Global)': [average_degree_mean],
        'Global Efficiency': [global_efficiency_mean],
        'Average Shortest Path Length': [shortest_path_length_mean],
        'Clustering Coefficient': [clustering_coefficient_mean],
        'Modularity' :[modularity_meam]
    })

    df = pd.concat([df, averages_row], ignore_index=True)
    df.to_csv(file_path, index=False)


    # Show success message
    #messagebox.showinfo("Success", "Data has been exported and averages calculated successfully.")


def measures_to_excel1(results_file_path, segment_file_path, segment_number, selected_threshold):
    try:
        matrix = load_connectivity_matrix1(segment_file_path)
        print(f"Loaded matrix for segment {segment_number}:")
       
        thresholded_matrix = apply_threshold1(matrix, float(selected_threshold))
        print(f"Thresholded matrix for segment {segment_number}:")
        

        G = build_graph1(thresholded_matrix)
        print(f"Graph info for segment {segment_number}: Nodes - {len(G.nodes)}, Edges - {len(G.edges)}")
        average_degree = np.mean([d for n, d in G.degree()]) if G else 0
        print(average_degree)
        global_efficiency = calculate_global_efficiency1(G)  
        print(global_efficiency)
        clustering_coeff = nx.average_clustering(G) if G else 0
        print(clustering_coeff)
        shortest_path_length = calculate_average_shortest_path_length1(G)if G else 0
       
        modularity= calculate_modularity1(G)
        new_row = pd.DataFrame({
            'Segment_number': [segment_number],
            'Average Degree (Global)': [average_degree],
            'Global Efficiency': [global_efficiency],
            'Average Shortest Path Length': [shortest_path_length],
            'Clustering Coefficient': [clustering_coeff],
            'Modularity': [modularity]
        })

        with open(results_file_path, 'a') as f:
            new_row.to_csv(f, index=False, header=False)

    except Exception as e:
        print(f"An error occurred during graph measures calculation for segment {segment_number}: {e}")


def calculate_average_shortest_path_length1(G):
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
    

    
def get_segment_count1(main_folder_path, selected_analysis_type, selected_patient):
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

def calculate_modularity1(G):
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


def load_connectivity_matrix1(file_path):
    return pd.read_csv(file_path, header=None, skiprows=1) 

def apply_threshold1(matrix, threshold):
    significant_connections = np.abs(matrix) > threshold
    return np.where(significant_connections, matrix, 0)


def build_graph1(matrix):
    G = nx.Graph()
    n = matrix.shape[0]  # Number of rows
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n): 
            if matrix[i, j] != 0:
                G.add_edge(i, j, weight=matrix[i, j])
    return G

import networkx as nx

def calculate_global_efficiency1(G):
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