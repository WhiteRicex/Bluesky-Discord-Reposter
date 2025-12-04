import os
import requests
import time
import json
import ffmpeg

import discord
from discord import SyncWebhook

from atproto import Client
from dotenv import load_dotenv

load_dotenv()
client = Client()
client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"))

with open("settings.json", "r") as file:
    settingsData = json.load(file)
    actors = settingsData["actors"]
    print("actors loaded: ", actors)

    webhook_url = settingsData["webhook"]
    
url = "https://public.api.bsky.app/"

contentIDFile = "contentID.json"

starttime = time.monotonic()

def main():
    with open(contentIDFile, "r") as file:
        contentIDdata = json.load(file)
        print("checking caches: ", contentIDdata["actors"])

    for actor in actors:
        print("checking actor: ", actor)

        getAuthorFeed = requests.get(url + "/xrpc/app.bsky.feed.getAuthorFeed", params={"actor": actor, "limit": "1", "filter": "posts_with_media"})
        print("### RESPONSE CODE ###\n", getAuthorFeed.status_code)

        if(getAuthorFeed.status_code == 200):
            print("get author feed ok!")

            authorFeedData = getAuthorFeed.json()
            contentID = authorFeedData["feed"][0]["post"]["cid"]
            
            send_image = True

            # check is image
            if(authorFeedData["feed"][0]["post"]["embed"]["$type"] == "app.bsky.embed.images#view"):
                print("image!")
                image = authorFeedData["feed"][0]["post"]["embed"]["images"][0]["fullsize"]
            else:
                print("video!")
                send_image = False

                if(os.path.isfile("video.mp4")):
                    os.remove("video.mp4")

                video_url = authorFeedData["feed"][0]["post"]["embed"]["playlist"]

                stream = ffmpeg.input(video_url)
                stream = ffmpeg.output(stream, "video.mp4")
                ffmpeg.run(stream)

                with open("video.mp4", "rb") as f:
                    image = discord.File(f)

            print("contentID", contentID)

            # add missing key
            if(contentIDdata["actors"].get(actor) == None):
                contentIDdata["actors"][actor]=""
            
            if(contentIDdata["actors"][actor] != contentID):
                with open(contentIDFile, "w") as file:
                    print("no match! posting new")

                    contentIDdata["actors"][actor] = contentID
                    json.dump(contentIDdata, file)

                    syncWebhook = SyncWebhook.from_url(webhook_url)
                    
                    if(send_image):
                        syncWebhook.send(image)
                    else:
                        syncWebhook.send(file=image)

while(True):
    main()
    print("tick")
    time.sleep(60.0 - ((time.monotonic() - starttime) % 60.0))