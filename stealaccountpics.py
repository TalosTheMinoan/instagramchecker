import logging
from instaloader import Instaloader, Profile

# Configure logging
logging.basicConfig(filename='instagram_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Creating an instance of the Instaloader class
bot = Instaloader()

# Loading a profile from an Instagram handle
profile = Profile.from_username(bot.context, '_kyriakos4')

# Log the profile information
logging.info("Username: %s", profile.username)
logging.info("User ID: %s", profile.userid)
logging.info("Number of Posts: %s", profile.mediacount)
logging.info("Followers Count: %s", profile.followers)
logging.info("Following Count: %s", profile.followees)
logging.info("Bio: %s", profile.biography)
logging.info("External URL: %s", profile.external_url)
logging.info("")

# Save profile information to a file
with open('profile_info.txt', 'w', encoding='utf-8') as profile_file:
    profile_file.write(f"Username: {profile.username}\n")
    profile_file.write(f"User ID: {profile.userid}\n")
    profile_file.write(f"Number of Posts: {profile.mediacount}\n")
    profile_file.write(f"Followers Count: {profile.followers}\n")
    profile_file.write(f"Following Count: {profile.followees}\n")
    profile_file.write(f"Bio: {profile.biography}\n")
    profile_file.write(f"External URL: {profile.external_url}\n")

# Download Files
logging.info("Download Files: ")

def download_posts_and_videos(username):
    L = Instaloader()
    profile = Profile.from_username(L.context, username)

    # For Loop to download posts
    for post in profile.get_posts():
        filename = post.date_utc.strftime('%Y-%m-%d %H-%M-%S')
        if post.is_video:
            L.download_post(post, target=filename)
            logging.info("Downloaded: %s.mp4", filename)
        else:
            L.download_post(post, target=filename)
            logging.info("Downloaded: %s.jpg", filename)

username = "_kyriakos4"  # enter the username of the target account
download_posts_and_videos(username)
