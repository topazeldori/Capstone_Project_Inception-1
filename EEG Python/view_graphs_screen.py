import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess  # Ensure subprocess is imported
from ShowData import get_segment_count, process_segment, build_community_detection, build_graph_measures  # Import necessary functions
import sys
import os
import glob

selected_analysis_type = sys.argv[1]
selected_threshold = float(sys.argv[2])  
selected_patient = sys.argv[3]

def open_view_graphs_screen(master):
    view_graphs_window = tk.Toplevel(master)
    view_graphs_window.title("Analysis networks in brain recordings")
    view_graphs_window.geometry("1200x600")  
    view_graphs_window.configure(bg='white')

    title_label = tk.Label(view_graphs_window, text="Analysis networks in brain recordings", font=("Georgia", 20, "bold"), bg='white', fg='#6A5ACD')
    title_label.pack(pady=(10, 20))
    subtitle_label = tk.Label(view_graphs_window, text="View Patient Graphs", font=("Arial", 18), bg='white', fg='grey')
    subtitle_label.pack(pady=(10, 30))
    subtitle_text = f"{selected_analysis_type}: {selected_patient} threshold {selected_threshold}"
    subtitle_label = tk.Label(view_graphs_window, text=subtitle_text, font=("Arial", 15), bg='white', fg='grey')
    subtitle_label.pack(pady=(10, 35))
    logout_label = tk.Label(view_graphs_window, text="Logout|Hello", font=("Arial", 14), bg='white', fg='black', cursor="hand2")
    logout_label.place(relx=0.01, rely=0.01)
    logout_label.bind("<Button-1>", lambda event: logout(view_graphs_window))

    try:
        logo_path = "logobrain.png" 
        img = Image.open(logo_path)
        img = img.resize((80, 80), Image.Resampling.LANCZOS)
        brain_image = ImageTk.PhotoImage(img)
        brain_image_label = tk.Label(view_graphs_window, image=brain_image, bg='white')
        brain_image_label.image = brain_image
        brain_image_label.place(relx=0.95, rely=0.01, anchor='ne')
    except Exception as e:
        print("Error loading or resizing logo image:", e)

    patient_label = tk.Label(view_graphs_window, text="Select a section:", font=("Arial", 12), bg='white')
    patient_label.place(relx=0.05, rely=0.3)
    patient_var = tk.StringVar()

    folder_path = "C:\\EEG Python\\creatdata"  
    num_segments = get_segment_count(folder_path)
    segment_values = [f"Segment {i+1}" for i in range(num_segments)]
    patient_dropdown = ttk.Combobox(view_graphs_window, textvariable=patient_var, values=segment_values, state="readonly")
    patient_dropdown.place(relx=0.05, rely=0.4, width=200)

    # Frame for displaying patient graph
    patient_graph_frame = tk.Frame(view_graphs_window, bg='white')
    patient_graph_frame.place(relx=0.3, rely=0.4, relwidth=0.65, relheight=0.65)

    # Frame for displaying community detection graph
    community_frame = tk.Frame(view_graphs_window, bg='white')
    community_frame.place(relx=0.3, rely=0.4, relwidth=0.65, relheight=0.65)
    community_frame.place_forget()  # Hide by default

    # Frame for displaying graph measures
    measures_frame = tk.Frame(view_graphs_window, bg='white')
    measures_frame.place(relx=0.3, rely=0.4, relwidth=0.65, relheight=0.65)
    measures_frame.place_forget() 

    def on_segment_select(event):
        target_folder_pattern = f"{selected_analysis_type}_{selected_patient}*"
        base_folder_path = os.path.join(folder_path, target_folder_pattern)
        matching_folders = glob.glob(base_folder_path)

        if not matching_folders:
            print(f"No folder found for {selected_analysis_type}_{selected_patient}")
            return

        full_folder_path = matching_folders[0]
        segment_full_name = patient_dropdown.get()
        segment_number = segment_full_name.split()[1]
        pattern = f"segment_{segment_number}_{selected_patient}*_*_connectivity.csv"
        matching_files = glob.glob(os.path.join(full_folder_path, pattern))

        if not matching_files:
            print(f"No connectivity file found for segment {segment_number}")
            return

        segment_file_path = matching_files[0]
        process_segment(segment_file_path, patient_graph_frame, float(selected_threshold))
        community_frame.place_forget()
        measures_frame.place_forget()
        patient_graph_frame.place(relx=0.3, rely=0.3, relwidth=0.65, relheight=0.65)  # Show the patient graph frame

    patient_dropdown.bind("<<ComboboxSelected>>", on_segment_select)

    def handle_community_detection():
        target_folder_pattern = f"{selected_analysis_type}_{selected_patient}*"
        base_folder_path = os.path.join(folder_path, target_folder_pattern)
        matching_folders = glob.glob(base_folder_path)

        if not matching_folders:
            print(f"No folder found for {selected_analysis_type}_{selected_patient}")
            return

        full_folder_path = matching_folders[0]
        segment_full_name = patient_dropdown.get()
        if segment_full_name: 
            segment_number = segment_full_name.split()[1]

            pattern = f"segment_{segment_number}_{selected_patient}*_*_connectivity.csv"
            matching_files = glob.glob(os.path.join(full_folder_path, pattern))

            if matching_files:
                segment_file_path = matching_files[0]
                build_community_detection(segment_file_path, community_frame, selected_threshold)
                patient_graph_frame.place_forget()  # Hide the patient graph frame
                measures_frame.place_forget()  # Hide the measures frame
                community_frame.place(relx=0.3, rely=0.3, relwidth=0.65, relheight=0.65)  # Show the community frame
            else:
                print(f"No file found for community detection on segment {segment_number}")

    community_button = tk.Button(view_graphs_window, text="View community detection", command=handle_community_detection, font=("Arial", 12), bg='white')
    community_button.place(relx=0.05, rely=0.6, width=200)

    def handle_graph_measures():
        target_folder_pattern = f"{selected_analysis_type}_{selected_patient}*"
        base_folder_path = os.path.join(folder_path, target_folder_pattern)
        matching_folders = glob.glob(base_folder_path)

        if not matching_folders:
            print(f"No folder found for {selected_analysis_type}_{selected_patient}")
            return

        full_folder_path = matching_folders[0]
        segment_full_name = patient_dropdown.get()
        if segment_full_name:  
            segment_number = segment_full_name.split()[1]

            pattern = f"segment_{segment_number}_{selected_patient}*_*_connectivity.csv"
            matching_files = glob.glob(os.path.join(full_folder_path, pattern))

            if matching_files:
                segment_file_path = matching_files[0]
                build_graph_measures(segment_file_path, measures_frame, selected_threshold)
                patient_graph_frame.place_forget()  # Hide the patient graph frame
                community_frame.place_forget()  # Hide the community frame
                measures_frame.place(relx=0.3, rely=0.3, relwidth=0.65, relheight=0.65)  # Show the measures frame
            else:
                print(f"No file found for graph measures on segment {segment_number}")

    graph_measures_button = tk.Button(view_graphs_window, text="View Graph Measures", command=handle_graph_measures, font=("Arial", 12), bg='white')
    graph_measures_button.place(relx=0.05, rely=0.7, width=200)

    back_button = tk.Button(view_graphs_window, text="Back", command=lambda: back_to_menu(view_graphs_window), font=("Arial", 12), bg='#6A5ACD', fg='white')
    back_button.place(relx=0.05, rely=0.9)

def logout(child_window):
    child_window.destroy()
    subprocess.call(["python", "go.py"]) 

def back_to_menu(view_graphs_window):
    view_graphs_window.destroy()
    subprocess.call(["python", "menu.py", selected_analysis_type, str(selected_threshold), selected_patient])  # Pass the global variables back to menu.py

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  
    open_view_graphs_screen(root)
    root.mainloop()