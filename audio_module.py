'''

THIS SCRIPT MANAGE THE AUDIO DOWNLOADING FEATURES

'''

# Libraries
import sys
import os
from pathlib import Path
import re
import moviepy as mp
from yt_dlp import YoutubeDL # -> import the yt_dlp library
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import threading
import time

# Ensures the icon is found by Pyinstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Manage the audio tab
def _audio_tab(notebook):

    # Loads the audio tab icon
    icon_path = resource_path("icons/audio_icon.png")

    # Create a new tab
    notebook.add("Audio Downloader")
    audio_tab = notebook.tab("Audio Downloader")

    # Loads the icon and prevents garbage collection to delete it
    image = ctk.CTkImage(light_image=Image.open(icon_path), size=(24, 24))
    label = ctk.CTkLabel(audio_tab, text="Audio Downloader", image=image, compound="left")
    label.pack(pady=10)
    audio_tab.image = image

    # UI to enter the video / playlist URL
    url_label = ctk.CTkLabel(audio_tab, text="Enter Video/Playlist URL:")
    url_label.pack(pady=5)
    url_entry = ctk.CTkEntry(audio_tab, width=300)
    url_entry.pack(pady=5)
    
    # Create the progress bar
    progress_bar = ctk.CTkProgressBar(audio_tab)
    progress_bar.set(0)
    progress_bar.pack(pady=10)
    progress_bar.pack_forget()
    
    # Create a dropdown menu to select audio quality
    audio_quality_label = ctk.CTkLabel(audio_tab, text="Select Audio Quality:")
    audio_quality_label.pack(pady=5)
    audio_quality_dropdown = ctk.CTkComboBox(audio_tab, values=[
        "320",
        "256",
        "192", # Default
        "128"
        ])
    audio_quality_dropdown.set("192")
    audio_quality_dropdown.pack(pady=5)

    # Show the progress of the download
    def show_progress(val):
        progress_bar.set(val)
        progress_bar.update_idletasks()

    # Use the yt_dlp library to extract the audio of the video.
    def playlist_downloader():
        playlist_url = url_entry.get()

        # Ask user for output directory
        output_dir = filedialog.askdirectory(title="Select Download Folder")

        # If user does not choose, use the Default Download folder
        if not output_dir:
            output_dir = os.path.join(Path.home(), "Downloads")

        selected_quality = audio_quality_dropdown.get()

        if not playlist_url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            progress_bar.pack_forget()
            return

        ydlp_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': selected_quality,
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        }

        # Download the audio file and show errors if somthing fails
        def download_audio():
            try:
                progress_bar.pack()
                with YoutubeDL(ydlp_opts) as ydl:
                    ydl.download([playlist_url])
                show_progress(1.0)
                messagebox.showinfo("Download Complete!", f"Downloaded audio in {selected_quality} quality.")
            except Exception as e:
                messagebox.showerror("Download Failed", str(e))
            finally:
                time.sleep(1)
                progress_bar.pack_forget()
                show_progress(0)

        # Runs the download in a background thread to avoid the GUI freezing.
        threading.Thread(target=download_audio).start()

    # Create the download button
    download_audio_button = ctk.CTkButton(audio_tab, text="Download", command=playlist_downloader)
    download_audio_button.pack(pady=20)

