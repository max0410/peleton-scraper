# DISCLAIMER: This program will create a text file called "class_IDs", it will be very small but don't delete it. 

# SETTINGS

CLIENT_ID = ""                  # Type the gibberish under the app's name between the quotes.

CLIENT_SECRET = ""              # Type the gibberish labeled "secret" on the app between the quotes.

BOT_NAME = "Peleton Scraper"    # Feel free to change this, it won't affect anything.

TIME_TO_POST = 24               # The bot will post info this number of hours before a ride, feel free to change.

USERNAME = ""                   # The username of the bot account.

PASSWORD = ""                   # The password of the bot account.

SUBREDDIT = ""                  # Your subreddit you want the bot to post in.

# CODE

from bs4 import BeautifulSoup
import requests, praw
from datetime import datetime

reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=BOT_NAME,
                     username=USERNAME,
                     password=PASSWORD)

file = open("class_IDs.txt", "r+")
classIDs = file.readlines()
classIDs = list(map(lambda x: x.replace("\n",""), classIDs))
while True:
    r  = requests.get("https://studio.onepeloton.com/reserve/index.cfm?action=Reserve.chooseClass&site=1")
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    classes = soup.findAll("div", "scheduleBlock bookable")
    for cl in classes:
        info = {}
        Id = str(cl["data-classid"])
        if Id not in classIDs:
            
            info["date"] = soup.find("tr").findChildren("td")[cl.parent.parent.findChildren("td").index(cl.parent)].findChildren("span")[1].text
            info["name"] = cl.findChild("span", "scheduleClass pop").text.replace("\t","").replace("\n","")
            info["instructor"] = cl.findChild("span", "scheduleInstruc active").text.replace(" ","")
            info["time"] = " ".join(cl.findChild("span", "scheduleTime active").text.split()[:2])
            info["duration"] = cl.findChild("span", "classlength").text
            info["link"] = "https://studio.onepeloton.com/reserve/" + cl.findChild("a")["href"]
            
            mo = int(info["date"][0])
            d = int(info["date"].split(".")[1])
            h = int(info["time"][0])
            if info["time"][-2:] == "PM":
                h += 12
            m = int(info["time"].split(":")[1][:3])

            if ( datetime.now().replace(month=mo, day=d, hour=h, minute=m) - datetime.now()).total_seconds() <= TIME_TO_POST*60*60:
                text = "["+ info["date"] +"] "+ info["name"] + " with "+ info["instructor"] + " at "+ info["time"] + " for "+ info["duration"] + "s."
                reddit.subreddit(SUBREDDIT).submit(title="text", url=info["url"])
                classIDs.append(Id)
                file.write(Id+"\n")

