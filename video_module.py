'''

THIS SCRIPT MANAGE THE VIDEO DOWNLOADING FEATURES

'''

# Libraries
import sys
import os
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from yt_dlp import YoutubeDL # -> import the yt_dlp library
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

# Manage the video tab
def _video_tab(notebook):

    # Loads the audio tab icon
    icon_path = resource_path("icons/video_icon.png")

    # Create a new tab
    notebook.add("Video Downloader")
    video_tab = notebook.tab("Video Downloader")

    # Loads the icon and prevents garbage collection to delete it
    image = ctk.CTkImage(light_image=Image.open(icon_path), size=(24, 24))
    label = ctk.CTkLabel(video_tab, text="Video Downloader", image=image, compound="left")
    label.pack(pady=10)
    video_tab.image = image

    # UI to enter the video / playlist URL
    video_url_label = ctk.CTkLabel(video_tab, text="Enter Video/Playlist URL:")
    video_url_label.pack(pady=5)
    video_url_entry = ctk.CTkEntry(video_tab, width=300)
    video_url_entry.pack(pady=5)

    # Create the progress bar
    progress_bar = ctk.CTkProgressBar(video_tab)
    progress_bar.set(0)
    progress_bar.pack(pady=10)
    progress_bar.pack_forget()

    # Create a dropdown menu to select video quality
    video_quality_label = ctk.CTkLabel(video_tab, text="Select Video Quality:")
    video_quality_label.pack(pady=5)
    video_quality_var = ctk.StringVar()

    #video_quality_dropdown = ctk.CTkComboBox(video_tab, textvariable=video_quality_var)
    video_quality_dropdown = ctk.CTkComboBox(video_tab, values= [
        "4320p",  # 8K
        "2160p", # 4K
        "1440p", # 2K
        "1080p", # FHD
        "720p",  # HD
        "480p",  # SD+
        "360p",  # SD
        "240p",  # Low SD
        "144p"   # Very Low
        ])
    
    video_quality_dropdown.set("1080p")  # Default to 1080p
    video_quality_dropdown.pack(pady=5)

    
    # Show the progress of the download
    def download_video():
        selected_quality = video_quality_dropdown.get()
        max_height = int(selected_quality.replace("p", ""))

        def show_progress(val):
            progress_bar.set(val)
            progress_bar.update_idletasks()

        progress_bar.pack()
        show_progress(0.1)

        url = video_url_entry.get()

        # Ask user for output directory
        output_dir = filedialog.askdirectory(title="Select Download Folder")

        # If user does not choose, use the Default Download folder
        if not output_dir:
            output_dir = os.path.join(Path.home(), "Downloads")

        

        # Check if the URL is not empty
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            progress_bar.pack_forget()
            return

        
        # FFmpeg path
        def ffmpeg_location():
            # Intenta primero con el ejecutable en la raíz del proyecto
            current_dir = os.path.dirname(os.path.abspath(__file__))
            local_ffmpeg = os.path.join(current_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            if os.path.isfile(local_ffmpeg):
                return local_ffmpeg

            # Busca en el PATH
            if shutil.which("ffmpeg"):
                return "ffmpeg"

            # AppImage (Linux portable)
            appdir = os.environ.get("APPDIR", None)
            if appdir:
                return os.path.join(appdir, "usr", "bin", "ffmpeg")

            raise EnvironmentError(
                "FFmpeg is not available. Please add the FFmpeg files inside the PyTube Downloader root directory."
            )

        # Configure yt-dlp options based on selected video quality
        ydl_opts = {
            #'ffmpeg_location' : os.path.join(os.environ["APPDIR"], "usr", "bin"), 
            'ffmpeg_location' : ffmpeg_location(),
            'format': f"bestvideo[ext=mp4][height<={max_height}]+bestaudio[ext=m4a]/best[height<={max_height}]",
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'merge_output_format' : 'mp4',
            'postprocessor' : [{
                #'key' : 'FFmpegVideoConvertor',
                'key' : 'FFmpegMerger',
                #'preferedformat' : 'mp4',
                }],
                'hls_prefer_native' : True,
                'hls_use_mpgets' : True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

                progress_bar.set(1)
        
            # Show confirmation message once download is complete
            messagebox.showinfo("Download Complete!", f"Downloaded video in {selected_quality} quality.")
        except Exception as e:
            print(f"Error downloading video: {e}")
            messagebox.showerror("Download Failed", str(e))

        finally:
            time.sleep(1)
            progress_bar.pack_forget()

    # Runs the download in the background thread to avoid the GUI freezing.
    def start_download_thread():
        threading.Thread(target=download_video, daemon=True).start()

    # Buttons manager
    download_video_button = ctk.CTkButton(video_tab, text="Download", command=start_download_thread)
    download_video_button.pack(pady=20)
