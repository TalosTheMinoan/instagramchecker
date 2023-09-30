import logging
import os
import traceback
import random
import string
from instaloader import Instaloader, Profile
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog

# Function to generate a random error code
def generate_error_key():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

# Configure the root logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')




# Create a logger for error logs
error_logger = logging.getLogger('error')
error_handler = logging.FileHandler('error.log')
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)

# Create a logger for Instagram profile logs
profile_info_logger = logging.getLogger('profile_info')
profile_info_handler = logging.FileHandler('profile_info.txt')
profile_info_formatter = logging.Formatter('%(asctime)s - %(message)s')
profile_info_handler.setFormatter(profile_info_formatter)
profile_info_logger.addHandler(profile_info_handler)

def view_error_code(error_key):
    error_popup = tk.Toplevel(root)
    error_popup.title("Error Code")
    error_label = ttk.Label(error_popup, text=f"Error Key: {error_key}", font=("Arial", 12), foreground="red")
    error_label.pack(padx=10, pady=10)

def clear_error_code():
    error_code_button.pack_forget()

def get_instagram_username():
    username = simpledialog.askstring("Input", "Enter Instagram username:")
    return username

def select_download_folder():
    folder_path = filedialog.askdirectory()
    download_folder_label.config(text=f"Download Folder: {folder_path}")
    global download_path
    download_path = folder_path

# Function to handle download preferences
def download_preferences():
    global download_preference
    download_preference = simpledialog.askstring("Download Preference", "Enter 'Images', 'Videos', 'All', or 'Single Post':")
    if download_preference and download_preference.lower() not in ['images', 'videos', 'all', 'single post']:
        messagebox.showerror("Error", "Invalid download preference. Please enter 'Images', 'Videos', 'All', or 'Single Post'.")
        download_preferences()

def download_posts_and_videos(username):
    if not download_path:
        messagebox.showerror("Error", "Please select a download folder.")
        return

    L = Instaloader()
    profile = Profile.from_username(L.context, username)

    total_posts = profile.mediacount
    current_post = 0
    error_count = 0

    media_dir = os.path.join(download_path, profile.username)
    os.makedirs(media_dir, exist_ok=True)

    # Add information about private and verified status to the profile_info.txt log
    profile_info_log_file = os.path.join(download_path, "profile_info.txt")
    with open(profile_info_log_file, "w", encoding="utf-8") as profile_info_file:
        profile_info_file.write(f"Username: {profile.username}\n")
        profile_info_file.write(f"Full Name: {profile.full_name}\n")
        profile_info_file.write(f"ID: {profile.userid}\n")
        profile_info_file.write(f"Bio: {profile.biography}\n")
        profile_info_file.write(f"Is Private: {profile.is_private}\n")
        profile_info_file.write(f"Is Verified: {profile.is_verified}\n")

    loading_label = ttk.Label(root, text="Loading...", font=("Arial", 14))
    loading_label.pack(pady=5)

    for post in profile.get_posts():
        try:
            filename = post.date_utc.strftime('%Y-%m-%d %H-%M-%S')
            target_path = os.path.join(media_dir, filename)
            
            if download_preference.lower() == "images" and not post.is_video:
                L.download_post(post, target=target_path)
                profile_info_logger.info("Downloaded: %s.jpg - Post Timestamp: %s - Post URL: https://www.instagram.com/p/%s/", filename, post.date_utc.strftime('%Y-%m-%d %H:%M:%S'), post.shortcode)
            elif download_preference.lower() == "videos" and post.is_video:
                L.download_post(post, target=target_path)
                profile_info_logger.info("Downloaded: %s.mp4 - Post Timestamp: %s - Post URL: https://www.instagram.com/p/%s/", filename, post.date_utc.strftime('%Y-%m-%d %H:%M:%S'), post.shortcode)
            elif download_preference.lower() == "all":
                L.download_post(post, target=target_path)
                if post.is_video:
                    profile_info_logger.info("Downloaded: %s.mp4 - Post Timestamp: %s - Post URL: https://www.instagram.com/p/%s/", filename, post.date_utc.strftime('%Y-%m-%d %H:%M:%S'), post.shortcode)
                else:
                    profile_info_logger.info("Downloaded: %s.jpg - Post Timestamp: %s - Post URL: https://www.instagram.com/p/%s/", filename, post.date_utc.strftime('%Y-%m-%d %H:%M:%S'), post.shortcode)
            elif download_preference.lower() == "single post":
                post_url = simpledialog.askstring("Single Post URL", "Enter the URL of the post you want to download:")
                if post_url:
                    L.download_post(post_url, target=target_path)
                    if post.is_video:
                        profile_info_logger.info("Downloaded: %s.mp4 - Post Timestamp: %s - Post URL: %s", filename, post.date_utc.strftime('%Y-%m-%d %H:%M:%S'), post_url)
                    else:
                        profile_info_logger.info("Downloaded: %s.jpg - Post Timestamp: %s - Post URL: %s", filename, post.date_utc.strftime('%Y-%m-%d %H:%M:%S'), post_url)

            hashtags = ', '.join(post.caption_hashtags)
            mentions = ', '.join(post.caption_mentions)
            profile_info_logger.info("Hashtags: %s - Mentions: %s", hashtags, mentions)
            profile_info_logger.info("Caption: %s", post.caption)

            profile_info_logger.info("Likes: %s - Comments: %s", post.likes, post.comments)
            engagement_rate = (post.likes + post.comments) / profile.followers * 100
            profile_info_logger.info("Engagement Rate: %.2f%%", engagement_rate)

            current_post += 1
            progress = current_post / total_posts * 100
            progress_bar["value"] = progress
            progress_label.config(text=f"Downloading... {progress:.2f}%")
            post_count_label.config(text=f"Posts Downloaded: {current_post}/{total_posts}")
            engagement_rate_label.config(text=f"Engagement Rate: {engagement_rate:.2f}%")

        except Exception as e:
            error_count += 1
            error_key = generate_error_key()
            error_message = f"Error downloading post {post.shortcode}: {str(e)} (Error Key: {error_key})"
            error_logger.error(error_message)
            with open('error.log', 'a', encoding='utf-8') as errorlog_file:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                traceback_info = traceback.format_exc()
                errorlog_file.write(f"[ERROR] [{timestamp}] {error_message}\n")
                errorlog_file.write(f"Traceback Info:\n{traceback_info}\n")

    loading_label.pack_forget()
    if error_count == 0:
        messagebox.showinfo("Download Complete", "Profile download is complete!")
    else:
        messagebox.showinfo("Download Complete", f"Profile download is complete with {error_count} errors.")
        error_count_label.config(text=f"Errors Encountered: {error_count}")

def view_error_log():
    try:
        with open('error.log', 'r', encoding='utf-8') as errorlog_file:
            errorlog_text = errorlog_file.read()
        errorlog_window = tk.Toplevel(root)
        errorlog_window.title("Error Log")

        errorlog_textbox = tk.Text(errorlog_window, wrap=tk.WORD)
        errorlog_textbox.insert('1.0', errorlog_text)
        errorlog_textbox.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(errorlog_textbox, orient="vertical", command=errorlog_textbox.yview)
        scrollbar.pack(side="right", fill="y")
        errorlog_textbox.config(yscrollcommand=scrollbar.set)
    except FileNotFoundError:
        messagebox.showinfo("Error Log", "No errors logged yet.")

def clear_error_log():
    result = messagebox.askyesno("Clear Error Log", "Are you sure you want to clear the error log?")
    if result:
        with open('error.log', 'w', encoding='utf-8') as errorlog_file:
            errorlog_file.write("")
        messagebox.showinfo("Error Log Cleared", "Error log has been cleared.")
    else:
        messagebox.showinfo("Clear Error Log", "Error log was not cleared.")

# Create the main window
root = tk.Tk()
root.title("Instagram Profile Downloader")
root.geometry("800x500")

download_path = ""
download_preference = "all"  # Default to downloading all content

# Create and configure GUI elements
title_label = ttk.Label(root, text="Welcome to Instagram Profile Downloader", font=("Arial", 20, "bold"), foreground="blue")
title_label.pack(pady=10)

username_label = ttk.Label(root, text="Enter Instagram Username:", font=("Arial", 14))
username_label.pack(pady=5)

username_entry = ttk.Entry(root, font=("Arial", 14))
username_entry.pack(pady=5)

download_folder_button = ttk.Button(root, text="Select Download Folder", command=select_download_folder, style="Folder.TButton")
download_folder_button.pack(pady=5)

download_folder_label = ttk.Label(root, text="Download Folder: Not selected", font=("Arial", 12))
download_folder_label.pack(pady=5)

download_preference_button = ttk.Button(root, text="Set Download Preference", command=download_preferences, style="Folder.TButton")
download_preference_button.pack(pady=5)

download_button = ttk.Button(root, text="Download Profile", command=lambda: download_posts_and_videos(username_entry.get()), style="Download.TButton")
download_button.pack(pady=10)

error_log_button = ttk.Button(root, text="View Error Log", command=view_error_log, style="Error.TButton")
error_log_button.pack(pady=10)

clear_error_log_button = ttk.Button(root, text="Clear Error Log", command=clear_error_log, style="Error.TButton")
clear_error_log_button.pack(pady=10)

def show_tutorial():
    tutorial_text = """Welcome to Instagram Profile Downloader!

Follow these steps to download Instagram posts:
1. Enter the Instagram username in the provided field.
2. Click the 'Select Download Folder' button to choose where you want to save the downloaded content.
3. Click the 'Set Download Preference' button to specify your download preference. You can choose to download 'Images', 'Videos', 'All' content, or a 'Single Post'.
4. Click the 'Download Profile' button to start the download.
5. You can view any errors in the 'View Error Log' section, and clear the error log if needed.
6. Check the progress and details in the 'Progress' section.

Enjoy downloading Instagram posts!"""

    messagebox.showinfo("Tutorial", tutorial_text)

tutorial_button = ttk.Button(root, text="Tutorial", command=show_tutorial, style="Folder.TButton")
tutorial_button.pack(pady=10)

progress_label = ttk.Label(root, text="", font=("Arial", 14))
progress_label.pack(pady=10)

post_count_label = ttk.Label(root, text="", font=("Arial", 12))
post_count_label.pack(pady=5)

engagement_rate_label = ttk.Label(root, text="", font=("Arial", 12))
engagement_rate_label.pack(pady=5)

error_count_label = ttk.Label(root, text="", font=("Arial", 12))
error_count_label.pack(pady=5)

# Custom style for buttons
style = ttk.Style()
style.configure("Download.TButton", font=("Arial", 14, "bold"), foreground="green")
style.configure("Error.TButton", font=("Arial", 14, "bold"), foreground="red")
style.configure("Folder.TButton", font=("Arial", 14, "bold"))

# Custom style for labels
style.configure("Download.TLabel", font=("Arial", 12), foreground="green")
style.configure("Error.TLabel", font=("Arial", 12), foreground="red")

# Resize the Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
progress_bar.pack(pady=10)

# Center the window on the screen
root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = root.winfo_width()
window_height = root.winfo_height()
x_pos = (screen_width - window_width) // 2
y_pos = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

root.mainloop()
