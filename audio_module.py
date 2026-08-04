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
import shutil
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
    url_label = ctk.CTkLabel(audio_tab, text="Enter Video / Playlist URL:")
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

    def ffmpeg_location():
        # Try first to use the executable located in the root of the project
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg = os.path.join(current_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if os.path.isfile(local_ffmpeg):
            return local_ffmpeg
        
        # Serch in the path
        if shutil.which("ffmpeg"):
            return "ffmpeg"
        
        # AppImage (Linux portable)
        appdir = os.environ.get("APPDIR", None)
        if appdir:
            return os.path.join(appdir, "usr", "bin", "ffmpeg")
        
        raise EnvironmentError(
            "FFmpeg is not available. Please add the FFmpeg files inside the PyTube Downloader root directory."
                    )

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
            "ffmpeg_location": ffmpeg_location(),
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': selected_quality,
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        }

        # Download the audio file and show errors if something fails
        def download_audio():
            try:
                progress_bar.pack()
                with YoutubeDL(ydlp_opts) as ydl:
                    ydl.download([playlist_url])

                audio_tab.after(0, lambda: show_progress(1.0))
                audio_tab.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Download Complete!",
                        f"Download audio in {selected_quality} quality."
                    )
                )

            except Exception as e:
                audio_tab.after(
                    0,
                    lambda: messagebox.showerror(
                        "Download Failed",
                        str(e)
                    )
                )

            finally:
                audio_tab.after(
                    1000,
                    lambda: (
                        progress_bar.pack_forget(),
                        show_progress(0)
                    )
                )
                
        # Runs the download in a background thread to avoid the GUI freezing.
        threading.Thread(target=download_audio, daemon=True).start()

    # Create the download button
    download_audio_button = ctk.CTkButton(audio_tab, text="Download", command=playlist_downloader)
    download_audio_button.pack(pady=20)

