import os
import customtkinter as ctk
from tkinter import filedialog, Listbox, END
from PIL import Image
from customtkinter import CTkImage
import InterpreterRexi
import CompilerRexi

# Initialize CustomTkinter
ctk.set_appearance_mode("dark")  # Modes: "dark", "light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

# Create the main application window
app = ctk.CTk()
app.title("Rexi Language Editor")
app.geometry("1000x600")

current_directory = ""
switch_var = ctk.BooleanVar(value=False)  # False = désactivé par défaut
dynamic_text = ctk.StringVar(value="Interpreter Mode")
# Functions
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Rexi Files", "*.rexi"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            content = file.read()
            text_editor.delete("1.0", END)  # Clear the editor
            text_editor.insert("1.0", content)  # Load file content
        console.insert(END, f"Loaded file: {file_path}\n")  # Log to console

def toggle_mode():
    if switch_var.get():  # Si activé
        console.insert(END, "Mode activé : Compilateur\n")
        dynamic_text.set("Compiler Mode")
    else:  # Si désactivé
        console.insert(END, "Mode activé : Interpréteur\n")
        dynamic_text.set("Interpreter Mode")
def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".rexi", filetypes=[("Rexi Files", "*.rexi"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(text_editor.get("1.0", END))  # Save content to file
        console.insert(END, f"Saved file: {file_path}\n")  # Log to console

def run_code():
    source_code = text_editor.get("1.0", END).strip()  # Get all text from the editor
    console.insert(END, "Running Rexi code...\n\n")  # Log to console
    if source_code:
        if not switch_var.get() :
            out = InterpreterRexi.Run(source_code)  # Appel pour le mode interpréteur
        else:  # Mode compilateur
            out = CompilerRexi.Run(source_code)  # Exemple d'appel pour le compilateur
        console.insert(END, f"Code output:\n{out}")
        console.yview_moveto(1.0)
    else:
        console.insert(END, "No code to run.")
        console.yview_moveto(1.0)

def load_directory():
    global current_directory
    dir_path = filedialog.askdirectory()
    if dir_path:
        current_directory = dir_path
        file_list.delete(0, END)  # Clear current file list
        for file_name in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, file_name)):  # Show files only
                file_list.insert(END, file_name)  # Add files to the list
        console.insert(END, f"Loaded directory: {dir_path}\n")


def open_selected_file():
    try:
        global current_directory
        # Check if a directory is loaded
        if current_directory == "":
            console.insert(END, "No directory loaded. Please load a directory first.\n")
            return

        # Check if a file is selected
        selected_file = file_list.get(file_list.curselection())
        if not selected_file:
            console.insert(END, "No file selected. Please select a file from the list.\n")
            return

        # Construct the full file path
        file_path = os.path.join(current_directory, selected_file)

        # Open and read the file
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                content = file.read()
                text_editor.delete("1.0", END)  # Clear the editor
                text_editor.insert("1.0", content)  # Load file content
            console.insert(END, f"Opened file: {file_path}\n")
        else:
            console.insert(END, f"Error: File not found - {file_path}\n")
    except Exception as e:
        console.insert(END, f"Error: {e}\n")


# Buttons
button_frame = ctk.CTkFrame(app, corner_radius=10 )
button_frame.pack( fill="x" ,padx=20, pady=5 )

mode_switch = ctk.CTkSwitch(button_frame,text = "", variable=switch_var, onvalue=True, offvalue=False, command=toggle_mode)
mode_switch.pack(side="left", padx=0)
on = ctk.CTkLabel(button_frame, textvariable = dynamic_text)
on.pack(side = "left" , padx=0)
run_button = ctk.CTkButton(button_frame, text="Run Code", command=run_code ,width=20 , height= 20)
run_button.pack(side="right", padx=5)

save_button = ctk.CTkButton(button_frame, text="Save File", command=save_file ,width=20 , height= 20)
save_button.pack(side="right", padx=5)

open_button = ctk.CTkButton(button_frame, text="Open File", command=open_file ,width=20 , height= 20)
open_button.pack(side="right", padx=5)

# Layout
# Sidebar for File Explorer
sidebar = ctk.CTkFrame(app, width=200, corner_radius=10)
sidebar.pack(side="left", fill="y")


file_list_label = ctk.CTkLabel(sidebar, text="File Explorer" )
file_list_label.pack(pady=2)

file_list = Listbox(sidebar, height=35, width=40, bg="#333333", fg="white", selectbackground="#555555", highlightbackground="#444444",border = 0)
file_list.pack(pady=10, padx=5)


open_file_button = ctk.CTkButton(sidebar, text="Open selected", command=open_selected_file ,width=20 , height= 20)
open_file_button.pack(pady=3, padx=10)

load_dir_button = ctk.CTkButton(sidebar, text="Load directory", command=load_directory ,width=20 , height= 20)
load_dir_button.pack(pady=3, padx=10)

logo_image = Image.open(r"C:\Users\hp-pc\PycharmProjects\my_languge\logo rexi tr png.png")
logo_photo = CTkImage(logo_image ,size=(100, 100))
logo_label = ctk.CTkLabel(sidebar, image=logo_photo, text="")
logo_label.image = logo_photo  # Keep a reference to avoid garbage collection
logo_label.pack(padx=10)

# Main Text Editor
text_editor = ctk.CTkTextbox(app, width=550, height=390, corner_radius=10)
text_editor.pack(pady=10, padx=20, side="top", expand=True, fill="both")

# Console/Output Area
console_label = ctk.CTkLabel(app, text="Console Output")
console_label.pack(anchor="w", padx=20)

console = ctk.CTkTextbox(app, width=600, height=120, corner_radius=10, state="normal")
console.pack(pady=5, padx=20)



# Run the application
app.mainloop()
