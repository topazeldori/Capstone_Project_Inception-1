import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import subprocess
import sys
from Export_patient_Data import clac_all_psegment_measures

# Ensure that arguments are passed correctly
if len(sys.argv) < 4:
    print("Error: Missing required arguments")
    sys.exit(1)

selected_analysis_type = sys.argv[1]
selected_threshold = sys.argv[2]
selected_patient = sys.argv[3]

def open_menu(master):
    menu_window = tk.Toplevel(master)
    menu_window.title("Analysis networks in brain recordings")
    menu_window.geometry("838x445")
    menu_window.configure(bg='white')

    title_label = tk.Label(menu_window, text="Analysis networks in brain recordings", font=("Georgia", 20, "bold"), bg='white', fg='#6A5ACD')
    title_label.pack(pady=(10, 10))
    subtitle_label = tk.Label(menu_window, text="Menu", font=("Arial", 18), bg='white', fg='grey')
    subtitle_label.pack(pady=(10, 10))
    subtitle_text1 = f"{selected_analysis_type}: {selected_patient} threshold {selected_threshold}"
    subtitle_label1 = tk.Label(menu_window, text=subtitle_text1, font=("Arial", 15), bg='white', fg='grey')
    subtitle_label1.pack(pady=(5, 10))
    logout_label = tk.Label(menu_window, text="Logout|Hello", font=("Arial", 14), bg='white', fg='black', cursor="hand2")
    logout_label.place(relx=0.01, rely=0.01)
    logout_label.bind("<Button-1>", lambda event: logout(menu_window))

    back_button = tk.Button(menu_window, text="Back", command=lambda: back_to_Analyze(menu_window), font=("Arial", 12), bg='#6A5ACD', fg='white')
    back_button.place(relx=0.05, rely=0.9)

    logo_path = "logobrain.png"
    try:
        img = Image.open(logo_path)
        img = img.resize((80, 80), Image.Resampling.LANCZOS)
        brain_image = ImageTk.PhotoImage(img)
        brain_image_label = tk.Label(menu_window, image=brain_image, bg='white')
        brain_image_label.image = brain_image
        brain_image_label.place(relx=0.95, rely=0.01, anchor='ne')
    except Exception as e:
        print("Error loading or resizing logo image:", e)

    create_buttons(menu_window, master)

def create_buttons(menu_window, master):
    btn_view = tk.Button(menu_window, text="View Patients Graphs", font=("Calibri", 12, "bold"), bg='#6A5ACD', fg='white', padx=20, pady=10, command=lambda: open_new_window("view_graphs_screen.py", menu_window))
    btn_view.place(relx=0.1, rely=0.40, width=200, height=50)
    btn_analyze = tk.Button(menu_window, text="Export Patient Data", font=("Calibri", 12, "bold"), bg='#6A5ACD', fg='white', padx=20, pady=10, command=lambda: clac_all_psegment_measures(selected_analysis_type, selected_patient, float(selected_threshold)))
    btn_analyze.place(relx=0.6, rely=0.40, width=200, height=50)

def open_new_window(script_name, menu_window):
    subprocess.Popen(["python", script_name, selected_analysis_type, selected_threshold, selected_patient], shell=True)
    menu_window.destroy()  # Destroy the menu window as soon as the new window opens

def back_to_Analyze(menu_window):
    menu_window.destroy()
    subprocess.call(["python", "Analyze_graphs_screen.py"])  
def logout(menu_window):
    menu_window.destroy()
    subprocess.Popen(["python", "go.py"], shell=True)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_menu(root)
    root.mainloop()
