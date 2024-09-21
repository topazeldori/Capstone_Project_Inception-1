import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import Analyze_graphs_screen

def login_action():
    username = entry_username.get()
    password = entry_password.get()
    # Check credentials
    if username == "koraltopaz" and password == "1234":
        error_label.config(text="Login successful!", fg='green')
        root.withdraw()  # Hide the login window
        Analyze_graphs_screen.analyze_graphs_screen(root)  # Open the menu screen
    else:
        error_label.config(text="The username or password is incorrect.", fg='red')

root = tk.Tk()
root.title("Login")
root.geometry("800x500")
root.configure(bg='white')

title_font = ("Georgia", 20, "bold")
title_label = tk.Label(root, text="Welcome to analysis networks in\nbrain recordings", font=title_font, bg='white', fg='#7B68EE')
title_label.place(relx=0.2, rely=0.1, anchor='nw')

# Error message label
error_label = tk.Label(root, text="", font=("Calibri", 12), bg='white')
error_label.place(relx=0.5, rely=0.65, anchor='center')

# Load, resize, and display the PNG logo
logo_path = "logobrain.png"
try:
        img = Image.open(logo_path)
        img = img.resize((80, 80), Image.Resampling.LANCZOS)
        brain_image = ImageTk.PhotoImage(img)
        brain_image_label = tk.Label(root, image=brain_image, bg='white')
        brain_image_label.image = brain_image
        brain_image_label.place(relx=0.95, rely=0.01, anchor='ne')
except Exception as e:
        print("Error loading or resizing logo image:", e)


username_font = ("Calibri", 15)
username_label = tk.Label(root, text="User Name:", font=username_font, bg='white', fg='#333333')
username_label.place(relx=0.35, rely=0.4, anchor='e')
entry_username = tk.Entry(root, font=username_font, width=20)
entry_username.place(relx=0.35, rely=0.4, anchor='w')

password_label = tk.Label(root, text="Password:", font=username_font, bg='white', fg='#333333')
password_label.place(relx=0.35, rely=0.5, anchor='e')
entry_password = tk.Entry(root, font=username_font, show='*', width=20)
entry_password.place(relx=0.35, rely=0.5, anchor='w')

login_button = tk.Button(root, text="Login", command=login_action, font=("Calibri", 14, "bold"), bg='#7B68EE', fg='white', bd=0, padx=20, pady=10)
login_button.place(relx=0.45, rely=0.85, anchor='center')

root.mainloop()
