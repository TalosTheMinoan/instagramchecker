from instaloader import Instaloader, Profile

def download_posts_and_videos(username):
    L = Instaloader()
    profile =  Profile.from_username(L.context, username)
    for post in profile.get_posts():
        filename = post.date_utc.strftime('%Y=%m-%d %H=%M-%S')
        if post.is_video:
            L.download_post(post, target=filename)
            print(f"Downloaded: {filename}.mp4")
        else:
            L.download_post(post, target=filename)
            print(f"Downloaded: {filename}.jpg")

username = "addausername" #enter username of target account
download_posts_and_videos(username)  


