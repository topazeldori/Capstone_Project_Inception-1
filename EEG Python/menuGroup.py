import tkinter as tk
from tkinter import ttk, PhotoImage
from PIL import Image, ImageTk
import threading
import time
from GroupAnalyze import plot, data_group_func
import sys
import subprocess
from Export_group_data import clac_group_measures

selected_threshold = float(sys.argv[1])

def run_data_analysis(menu_window, plot_frame, progress_bar, loading_label, update_progress):
    def data_processing():
        adhd_averages, nonadhd_averages = data_group_func(selected_threshold, progress_callback=update_progress)
        menu_window.after(0, lambda: plot(adhd_averages, nonadhd_averages, plot_frame))
        
        # Remove the progress bar and loading label after plotting is complete
        menu_window.after(0, progress_bar.place_forget)
        menu_window.after(0, loading_label.place_forget)
        
        # Create and display the back button after plotting is complete
        menu_window.after(0, lambda: create_back_button(menu_window))
        # Create the calculate group measures button
        menu_window.after(0, lambda: create_export_button(menu_window))

    threading.Thread(target=data_processing).start()

def update_progress(progress):
    progress_bar['value'] = progress
    menu_window.update_idletasks()

def create_back_button(menu_window):
    back_button = tk.Button(menu_window, text="Back", command=lambda: back_to_Analyze(menu_window), font=("Arial", 12), bg='#6A5ACD', fg='white')
    back_button.place(relx=0.01, rely=0.95, anchor='sw')

def create_export_button(menu_window):
    export_button = tk.Button(menu_window, text="Export To Execl", command=lambda: clac_group_measures(), font=("Arial", 12), bg='#6A5ACD', fg='white')
    export_button.place(relx=0.20, rely=0.25, anchor='sw')


def open_menuGroup(master):
    global menu_window, progress_bar, loading_label
    menu_window = tk.Toplevel(master)
    menu_window.title("Analysis Group networks in brain recordings")
    menu_window.geometry("1200x600")
    menu_window.configure(bg='white')

    title_label = tk.Label(menu_window, text="Analysis networks in brain recordings", font=("Georgia", 20, "bold"), bg='white', fg='#6A5ACD')
    title_label.place(relx=0.5, rely=0.05, anchor='n')

    subtitle_label1 = tk.Label(menu_window, text=f"Threshold: {selected_threshold}", font=("Arial", 15), bg='white', fg='grey')
    subtitle_label1.place(relx=0.5, rely=0.12, anchor='n')

    loading_label = tk.Label(menu_window, text="It's a perfect time for a coffee refill!", font=("Arial", 14), bg='white', fg='black')
    loading_label.place(relx=0.5, rely=0.19, anchor='n')
    
    progress_bar = ttk.Progressbar(menu_window, orient='horizontal', length=500, mode='determinate')
    progress_bar.place(relx=0.5, rely=0.23, anchor='n')

    plot_frame = tk.Frame(menu_window, bg='white')
    plot_frame.place(relx=0.5, rely=0.27, relwidth=1.0, relheight=0.7, anchor='n')

    logout_label = tk.Label(menu_window, text="Logout|Hello", font=("Arial", 14), bg='white', fg='black', cursor="hand2")
    logout_label.place(relx=0.01, rely=0.01)
    logout_label.bind("<Button-1>", lambda event: logout(menu_window))

    threading.Thread(target=run_data_analysis, args=(menu_window, plot_frame, progress_bar, loading_label, update_progress)).start()
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

def back_to_Analyze(menu_window):
    menu_window.destroy()
    subprocess.call(["python", "Analyze_graphs_screen.py"])
def logout(menu_window):
    menu_window.destroy()
    subprocess.Popen(["python", "go.py"], shell=True)
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_menuGroup(root)
    root.mainloop()
