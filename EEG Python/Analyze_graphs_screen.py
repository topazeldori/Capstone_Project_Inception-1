import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import createData
#from GroupAnalyze import data_group_func
from GroupAnalyze import data_group_func
import json


# Global variables to store the selections
selected_analysis_type = None
selected_analysis_category = None
selected_threshold = None
selected_patient = None

def analyze_graphs_screen(master):
    global selected_analysis_type, selected_analysis_category, selected_threshold, selected_patient

    analysis_window = tk.Toplevel(master)
    analysis_window.title("Analysis networks in brain recordings")
    analysis_window.geometry("838x445")
    analysis_window.configure(bg='white')

    title_label = tk.Label(analysis_window, text="Analysis networks in brain recordings", font=("Georgia", 20, "bold"), bg='white', fg='#6A5ACD')
    title_label.pack(pady=(10, 20))
    logout_label = tk.Label(analysis_window, text="Logout|Hello", font=("Arial", 14), bg='white', fg='black', cursor="hand2")
    logout_label.place(relx=0.01, rely=0.01)
    logout_label.bind("<Button-1>", lambda event: logout(analysis_window))

    logo_path = "logobrain.png"
    try:
        img = Image.open(logo_path)
        img = img.resize((80, 80), Image.Resampling.LANCZOS)
        brain_image = ImageTk.PhotoImage(img)
        brain_image_label = tk.Label(analysis_window, image=brain_image, bg='white')
        brain_image_label.image = brain_image
        brain_image_label.place(relx=0.95, rely=0.01, anchor='ne')
    except Exception as e:
        print("Error loading or resizing logo image:", e)

    # Variables for selections
    analysis_type = tk.StringVar(value="")
    analysis_category = tk.StringVar(value="")

    # Analysis Category Selection
    group_analysis_btn = tk.Radiobutton(analysis_window, text="Group Analysis", variable=analysis_category, value="Group", font=("Arial", 12), bg='white',
                                        command=lambda: update_selection('category', analysis_category.get()))
    patient_analysis_btn = tk.Radiobutton(analysis_window, text="Patient Analysis", variable=analysis_category, value="Patient", font=("Arial", 12), bg='white',
                                          command=lambda: update_selection('category', analysis_category.get()))
    group_analysis_btn.place(relx=0.1, rely=0.3)
    patient_analysis_btn.place(relx=0.3, rely=0.3)

    # Analysis Type Selection
    adhd_btn = tk.Radiobutton(analysis_window, text="ADHD", variable=analysis_type, value="ADHD", font=("Arial", 12), bg='white',
                              command=lambda: update_selection('type', analysis_type.get()))
    nonadhd_btn = tk.Radiobutton(analysis_window, text="NonADHD", variable=analysis_type, value="NonADHD", font=("Arial", 12), bg='white',
                                 command=lambda: update_selection('type', analysis_type.get()))
    adhd_btn.place_forget()  # Hide initially
    nonadhd_btn.place_forget()  # Hide initially

    # Threshold Selection ComboBox
    threshold_label = tk.Label(analysis_window, text="Select Threshold:", font=("Arial", 12), bg='white')
    threshold_label.place(relx=0.1, rely=0.5)
    threshold_var = tk.StringVar()
    threshold_combobox = ttk.Combobox(analysis_window, textvariable=threshold_var, values=[0.4,0.5,0.6,0.7], state='readonly')
    threshold_combobox.bind("<<ComboboxSelected>>", lambda event: update_threshold(threshold_var.get()))
    threshold_combobox.place(relx=0.3, rely=0.5)

    # Patient Selection ComboBox
    patient_label = tk.Label(analysis_window, text="Select Patient:", font=("Arial", 12), bg='white')
    patient_label.place(relx=0.1, rely=0.6)
    patient_var = tk.StringVar()
    patient_combobox = ttk.Combobox(analysis_window, textvariable=patient_var, state='readonly')
    patient_combobox.place(relx=0.3, rely=0.6)
    patient_label.place_forget()  # Hide initially
    patient_combobox.place_forget()  # Hide initially

    error_label = tk.Label(analysis_window, text="", font=("Calibri", 12), bg='white')
    error_label.place(relx=0.5, rely=0.85, anchor='center')
    # 'Next' button that checks for completion before navigating
    next_button = tk.Button(analysis_window, text="Next", command=lambda: check_and_proceed(analysis_window, error_label), font=("Arial", 12), bg='#6A5ACD', fg='white')
    next_button.place(relx=0.9, rely=0.9, anchor='se')

    def update_selection(selection_type, value):
        global selected_analysis_type, selected_analysis_category
        if selection_type == 'type':
            selected_analysis_type = value
        elif selection_type == 'category':
            selected_analysis_category = value
        print(f"Updated {selection_type} to {value}")
        update_patient_options()

    def update_patient_options():
        if selected_analysis_category == "Patient":
            adhd_btn.place(relx=0.1, rely=0.4)
            nonadhd_btn.place(relx=0.3, rely=0.4)
            patient_label.place(relx=0.1, rely=0.55)
            patient_combobox.place(relx=0.3, rely=0.6)
            if selected_analysis_type == "ADHD":
                patient_combobox['values'] = [f"patient {i+1}" for i in range(61)]  # 61 patients for ADHD
            elif selected_analysis_type == "NonADHD":
                patient_combobox['values'] = [f"patient {i+1}" for i in range(60)]  # 60 patients for NonADHD
            patient_combobox.bind("<<ComboboxSelected>>", lambda event: update_patient(patient_combobox.get()))
        else:
            adhd_btn.place_forget()
            nonadhd_btn.place_forget()
            patient_label.place_forget()
            patient_combobox.place_forget()

    def update_patient(value):
        global selected_patient
        selected_patient = value
        print(f"Patient selected: {selected_patient}")

    def check_and_proceed(analysis_window, error_label):
        global selected_analysis_type, selected_patient, selected_threshold, selected_analysis_category
        if selected_analysis_category == "Patient":
            if not selected_analysis_type or not selected_patient or not selected_threshold:
                error_label.config(text="One or more of the fields are missing.", fg='red')
                return  # Stop the function if any field is missing
        else:  # Group Analysis
            if not selected_threshold:
                error_label.config(text="Threshold field is missing.", fg='red')
                return  # Stop the function if the threshold field is missing

        # If all fields are present, proceed with data processing
        error_label.config(text="")
        createData.main(selected_analysis_type, selected_patient)  # Call the function that does all processing

        # Close the current window and open the appropriate menu screen
        analysis_window.destroy()
        if selected_analysis_category == "Patient":
            subprocess.Popen(["python", "menu.py", selected_analysis_type, selected_threshold, selected_patient])  # Switch to menu screen for patient analysis
        else:
            #adhd_averages, nonadhd_averages = data_group_func(selected_threshold)
            #adhd_averages_str = json.dumps(adhd_averages)
            #nonadhd_averages_str = json.dumps(nonadhd_averages)
           # subprocess.Popen(["python", "menuGroup.py",selected_threshold,adhd_averages_str,nonadhd_averages_str]) # Switch to menu screen for group analysis
            subprocess.Popen(["python", "menuGroup.py",selected_threshold]) # Switch to menu screen for group analysis

            #subprocess.Popen(["python", "popmsg.py",selected_threshold]) # Switch to menu screen for group analysis

          
    def update_threshold(value):
        global selected_threshold
        selected_threshold = value
        print(f"Threshold selected: {selected_threshold}")

    def logout(analysis_window):
        analysis_window.destroy()
        subprocess.Popen(["python", "go.py"], shell=True)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main root window initially
    analyze_graphs_screen(root)
    root.mainloop()