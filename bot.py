import os
import requests
import time
import json

from discord import SyncWebhook

from atproto import Client
from dotenv import load_dotenv

load_dotenv()
client = Client()
client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"))

with open("settings.json", "r") as file:
    settingsData = json.load(file)
    author = settingsData["author"]
    webhook_url = settingsData["webhook"]
    
url = "https://public.api.bsky.app/"

contentIDFile = "contentID.json"

starttime = time.monotonic()

def main():
    with open(contentIDFile, "r") as file:
        contentIDdata = json.load(file)
        cacheID = contentIDdata["cid"]
        print(cacheID)

    getAuthorFeed = requests.get(url + "/xrpc/app.bsky.feed.getAuthorFeed", params={"actor": author, "limit": "1", "filter": "posts_with_media"})
    print("### RESPONSE CODE ###\n", getAuthorFeed.status_code)

    if(getAuthorFeed.status_code == 200):
        print("get author feed ok!")

        authorFeedData = getAuthorFeed.json()

        contentID = authorFeedData["feed"][0]["post"]["cid"]
        image = authorFeedData["feed"][0]["post"]["embed"]["images"][0]["fullsize"]
        print("contentID", contentID)

        if(cacheID != contentID):
            with open(contentIDFile, "w") as file:
                print("no match! posting new")

                contentIDdata["cid"] = contentID
                json.dump(contentIDdata, file)

                syncWebhook = SyncWebhook.from_url(webhook_url)
                syncWebhook.send(image)

while(True):
    main()
    print("tick")
    time.sleep(60.0 - ((time.monotonic() - starttime) % 60.0))