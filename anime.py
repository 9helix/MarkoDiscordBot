import requests
from bs4 import BeautifulSoup as bs
import datetime
from discord import Color
import time as ti

genres = {"Action": Color.brand_red(), "Adventure": Color.orange(), "Comedy": Color.gold(), "Drama": Color.purple(), "Sci-Fi": Color.green(), "Fantasy": Color.brand_green(),
          "Horror": Color.darker_grey(), "Romance": Color.fuchsia(), "Mystery": Color.dark_teal(), "Sports": Color.blue(), "Supernatural": Color.dark_green(), "Slice of Life": Color.yellow()}
wdays = {"Monday": 1, "Tuesday": 2, "Wednesday": 3,
         "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
newline = "\n"


class anime:
    def __init__(self, url):
        self.name = "Unknown"
        self.tag = ""
        self.episodes = "Unknown"
        self.cur_episodes = "Unknown"
        self.airing = "Unknown"
        self.broadcast = "Unknown"
        self.status = "Unknown"
        self.url = url
        self.season = "Unknown"
        self.cover_url = None
        self.countdown = ""
        self.genre = "Unknown"
        self.studio = "Unknown"
        self.genre1 = ""
        self.score = "N/A"
        self.max_episodes = 0

        self.unix_countdown = ""
        self.weekday = 0
        self.start = 0

    def fetch_data(self):
        page = requests.get(self.url)

        soup = bs(page.content, 'html.parser')
        stats = soup.find_all("span", {"class": "dark_text"})
        self.score = soup.find("div", {"class": "score-label"}).text
        if self.score != "N/A":
            self.score += "  ⭐"
        self.name = soup.find("h1", {"class": "title-name h1_bold_none"}).text
        if soup.find("p", {"class": "title-english title-inherit"}) != None:
            self.name = soup.find(
                "p", {"class": "title-english title-inherit"}).text
        self.tag = self.url[30:35]
        image = soup.find("img", {"itemprop": "image"})['data-src']
        self.cover_url = image
        for i in stats:
            if i.text == "Aired:":
                airing = i.parent.text
                self.airing = airing[10:-3]
                airing_start = self.airing[:self.airing.find(" to")]
            elif i.text == "Broadcast:":
                broadcast = i.parent.text
                if "Unknown" not in broadcast:

                    self.broadcast = broadcast[16:-7]
                    broadcast = broadcast[16:-13]

                    broadcast_hour = broadcast.split()[2]

                    self.weekday = wdays[broadcast.split()[0][:-1]]
                    # ep_time = [int(x) for x in broadcast_hour.split(":")]
                    ep_date = datetime.datetime.strptime(
                        broadcast_hour, "%H:%M")-datetime.timedelta(hours=9)
                    if datetime.datetime.strptime(broadcast_hour, "%H:%M").day != ep_date.day:
                        self.weekday -= 1
                        if self.weekday == 0:
                            self.weekday = 7
                    self.start = datetime.time(
                        hour=ep_date.hour, minute=ep_date.minute)

            elif i.text == "Episodes:":
                episodes = i.parent.text
                if episodes[13:-3] != "Unknown":
                    self.max_episodes = int(episodes[13:-3])

            elif i.text == "Status:":
                status = i.parent.text
                self.status = status[11:-3]
            elif i.text == "Premiered:":
                premiered = i.parent.text
                if "?" in premiered:
                    self.season = "Unknown"
                else:
                    self.season = premiered[12:-1]
            elif i.text == "Studios:":
                studio = i.parent.text
                if "None found" in studio:
                    self.studio = "Unknown"
                else:
                    self.studio = studio[10:-1]
            elif "Genre" in i.text:
                genre1 = i.findNext("span").text

                genre2 = i.findNext("span").findNext("span").text
                # print(genre1, genre2)
                self.genre1 = genre1
                if genre2 in genres:
                    self.genre = f"{genre1}, {genre2}"
                else:
                    self.genre = genre1
                break
                # self.season = premiered[12:-1]

        if self.status == "Currently Airing":
            self.status += "  🟢"
            time = airing_start+" "+broadcast_hour
            start = datetime.datetime.strptime(time, '%b %d, %Y %H:%M')
            start = start - datetime.timedelta(hours=9)
            self.cur_episodes = (datetime.datetime.utcnow()-start).days//7+1

            countdown = datetime.timedelta(days=(self.cur_episodes)*7)+start
            self.unix_countdown = int(ti.mktime(countdown.timetuple()))
            self.unix_countdown = f"\n\nEpisode {self.cur_episodes+1}: <t:{self.unix_countdown}:R>."

            self.episodes = f"{self.cur_episodes}/{self.max_episodes}"
        elif self.status == "Finished Airing":
            self.status += "  🔴"
        else:
            self.status += "  🟡"

    def __str__(self):
        return f"Score: {self.score}\nEpisodes: {self.episodes}\nStatus: {self.status}\nAiring: {self.airing}\n{f'Season: {self.season}'+newline if f'{self.season}'!='Unknown' else ''}Broadcast: {self.broadcast}\nGenre: {self.genre}\nStudio: {self.studio}\nURL: {self.url}{self.unix_countdown}"


"""
url = "https://myanimelist.net/anime/52635/Kami_no_Tou_2nd_Season?q=tower%20of%20god&cat=anime"
show = anime(url)
show.fetch_data()
print(show)"""

"""
with open('database/anime_dict.pkl', 'rb') as f:
    anime_dict = pickle.load(f)

#anime_dict[show.tag] = show.url
with open('database/anime_dict.pkl', 'wb') as f:
    pickle.dump(anime_dict, f)
for item in anime_dict:
    print(item, anime_dict[item])"""
# print(show)
