import requests
import time

from discord import SyncWebhook

with open("settings.txt", "r") as file:
    author = file.read()
    
url = "https://public.api.bsky.app/"

fileName = "contentID.txt"

webhook_url = "https://discord.com/api/webhooks/1445507968828313710/La-LnmcPd1JC_gnO4YijbQNwhTQISUBBmIc03b3bi3uV3M9dDAdjzkooDq0859v7cxT_"

starttime = time.monotonic()

def main():
    with open(fileName, "r") as file:
        cacheID = file.read()
        print(cacheID)

    getAuthorFeed = requests.get(url + "/xrpc/app.bsky.feed.getAuthorFeed", params={"actor": author, "limit": "1", "filter": "posts_with_media"})
    print("### RESPONSE CODE ###\n", getAuthorFeed.status_code)

    if(getAuthorFeed.status_code == 200):
        print("get author feed ok!")

        data = getAuthorFeed.json()

        contentID = data["feed"][0]["post"]["cid"]
        image = data["feed"][0]["post"]["embed"]["images"][0]["fullsize"]
        print("contentID", contentID)

        if(cacheID != contentID):
            with open(fileName, "w") as file:
                print("no match! posting new")

                syncWebhook = SyncWebhook.from_url(webhook_url)
                syncWebhook.send(image)

                file.truncate(0)
                file.write(contentID)

while(True):
    main()
    print("tick")
    time.sleep(60.0 - ((time.monotonic() - starttime) % 60.0))