from instaloader import Instaloader, Profile
import pandas as pd

## Creating an instance of the Instaloader class
bot = Instaloader()

## Loading a profile from an Instagram handle
profile = Profile.from_username(bot.context, '_kyriakos4')
print("Username: ", profile.username)
print("User ID: ", profile.userid)
print("Number of Posts: ", profile.mediacount)
print("Followers Count: ", profile.followers)
print("Following Count: ", profile.followees)
print("Bio: ", profile.biography)
print("External URL: ", profile.external_url)
print()
print("Download Files: ")

def download_posts_and_videos(username):
    L = Instaloader()
    profile =  Profile.from_username(L.context, username)

    # For Loop to download posts
    for post in profile.get_posts():
        filename = post.date_utc.strftime('%Y=%m-%d %H=%M-%S')
        if post.is_video:
            L.download_post(post, target=filename)
            print(f"Downloaded: {filename}.mp4")
        else:
            L.download_post(post, target=filename)
            print(f"Downloaded: {filename}.jpg")

username = "_kyriakos4" #enter username of target account
download_posts_and_videos(username)
