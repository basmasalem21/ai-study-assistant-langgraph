from googleapiclient.discovery import build
import html
import os
from dotenv import load_dotenv
# 1) API key
load_dotenv()
api_key = os.getenv("Youtube_API_KEY")

youtube = build("youtube", "v3", developerKey=api_key)

channel_id = "UC8butISFwT-Wl7EV0hUK0BQ"

channel_response = youtube.channels().list(
    part="contentDetails",
    id=channel_id
).execute()

uploads_playlist = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

next_page_token = None
index = 0

with open("video_resources.txt", "w", encoding="utf-8") as f:

    while True:

        videos = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist,
            maxResults=30,
            pageToken=next_page_token
        ).execute()

        for item in videos["items"]:

            title = html.unescape(item["snippet"]["title"])
            video_id = item["snippet"]["resourceId"]["videoId"]
            url = f"https://www.youtube.com/watch?v={video_id}"

            # thumbnail image
            thumbnail = item["snippet"]["thumbnails"]["high"]["url"]

            line = (
                f"{index}. {title}\n"
                f"Video: {url}\n"
                f"Thumbnail: {thumbnail}\n"
                f"{'-'*40}\n"
            )

            print(line)
            f.write(line)

            index += 1

        next_page_token = videos.get("nextPageToken")

        if not next_page_token:
            break