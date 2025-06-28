'''
-----------------------------------------------------
PyTube Downloader - Video/Audio Downloader Program
-----------------------------------------------------

Version: 2.5.0

Author: Joa98

Email: joaquinpuente98@gmail.com

------------------------------------
# Copyright (C) 2025 Joaquín Puente
# This file is licensed under the GNU General Public License v3.0.
# See https://www.gnu.org/licenses/gpl-3.0.html for more information.
------------------------------------
'''

# Libraries
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import ttk
from audio_module import _audio_tab
from video_module import _video_tab
import os
import sys


# Ensures the icon is found by Pyinstaller
def resource_path(icon_path):
    if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, icon_path)
    
    return os.path.join(os.path.abspath("."), icon_path)

# Main application window
def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme(resource_path("themes/purple_droid.json"))
    
    # Create the main application window
    root = ctk.CTk()
    root.title("PyTube Downloader")
    root.resizable(False, False)

    def show_disclaimer(root):
        disclaimer = ctk.CTkToplevel(root)
        disclaimer.title("Legal Notice")
        disclaimer.geometry("500x350")
        disclaimer.grab_set()  # blocks the rest of the UI until closed

        label_text = (
            "This program is intended for personal and educational use only.\n"
            "The developer is NOT responsible for any misuse of this application.\n\n"
            "License: GPL v3.0\n"
            "Source code available at:\n"
            "https://github.com/Joa98Dev/pytube-downloader\n"
        )

        label = ctk.CTkLabel(disclaimer, text=label_text, justify="left", wraplength=450)
        label.pack(pady=20, padx=20)

        def close_disclaimer():
            disclaimer.destroy()

        continue_button = ctk.CTkButton(disclaimer, text="Accept and Continue", command=close_disclaimer)
        continue_button.pack(pady=10)

    show_disclaimer(root)
 
    # Load the window icon
    icon_path = resource_path("icon.ico")
    try:
        root.iconbitmap(icon_path)
    except Exception as e:
        print("Can't find the icon:", e)

    # Create a tab
    notebook = ctk.CTkTabview(root)

    # Call the video and audio tabs
    _video_tab(notebook)
    _audio_tab(notebook)
    
    # Pack the tab into the main window
    notebook.pack(expand=True, fill='both')

    # Start Tkinter main loop
    root.mainloop()


# Ensures only runs if the script is direclty executed
if __name__ == "__main__":
    main()
