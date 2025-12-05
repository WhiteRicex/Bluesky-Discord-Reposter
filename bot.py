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
            
            # check for image
            if(authorFeedData["feed"][0]["post"]["embed"]["$type"] == "app.bsky.embed.images#view"):
                print("image!")
                for idx, i in enumerate(authorFeedData["feed"][0]["post"]["embed"]["images"]):
                    img_data = requests.get(i["fullsize"]).content
                    with open("output/"+str(idx)+".jpeg", 'wb') as f:
                        f.write(img_data)
            
            # check for video
            if(authorFeedData["feed"][0]["post"]["embed"]["$type"] == "app.bsky.embed.video#view"):
                print("video!")

                video_url = authorFeedData["feed"][0]["post"]["embed"]["playlist"]

                stream = ffmpeg.input(video_url)
                stream = ffmpeg.output(stream, "output/video.mp4")
                ffmpeg.run(stream)

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

                    files = [discord.File("output/"+str(f)) for f in os.listdir("output")]
                    syncWebhook.send(files=files)

            #clean up
            if(os.path.isdir("output")):
                os.system("rm -rf output")
                
            os.mkdir("output")

# check if we had leftover output 
if(os.path.isdir("output")):
    os.system("rm -rf output")

os.mkdir("output")

while(True):
    main()

    print("tick")
    time.sleep(60.0 - ((time.monotonic() - starttime) % 60.0))