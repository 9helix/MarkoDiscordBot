from jikanpy import Jikan
import datetime
from discord import Color
import time as ti
import pickle


def pkl_read(name: str):
    with open(f'database/{name}.pkl', 'rb') as f:
        data = pickle.load(f)
        return data


def pkl_write(name: str, data) -> None:
    with open(f'database/{name}.pkl', 'wb') as f:
        pickle.dump(data, f)


genres = {"Action": Color.brand_red(), "Adventure": Color.orange(), "Comedy": Color.gold(), "Drama": Color.purple(), "Sci-Fi": Color.green(), "Fantasy": Color.brand_green(),
          "Horror": Color.darker_grey(), "Romance": Color.fuchsia(), "Mystery": Color.dark_teal(), "Sports": Color.blue(), "Supernatural": Color.dark_green(), "Slice of Life": Color.yellow()}
wdays = {"Monday": 1, "Tuesday": 2, "Wednesday": 3,
         "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
newline = "\n"
delay_time = datetime.timedelta(hours=1, minutes=15)
jst_dif = datetime.timedelta(hours=9)
jikan = Jikan()


class anime:
    def __init__(self, code):
        self.id = code
        try:
            show = jikan.anime(self.id)
            self.success = True
        except:
            self.success = False
        # json.loads(requests.get("https://api.jikan.moe/v4/anime/49387").content.decode("utf-8")) - no wrapper needed method
        if self.success:
            show = show['data']
            if show['score'] == None:
                self.score = "N/A" + " ⭐"
            else:
                self.score = str(show['score'])+" ⭐"
            self.name = show['title_english']
            if self.name == None:
                self.name = show['title']
            self.cover_url = show["images"]["jpg"]["large_image_url"]
            self.url = show["url"]
            self.url = self.url.replace("\\", "")
            self.url = self.url[:self.url.find("/", 30)]
            self.airing = show["aired"]["string"]
            self.broadcast = show["broadcast"]['string']
            if show["broadcast"]['day'] != None:
                self.weekday = wdays[show['broadcast']['day'][:-1]]
                br_time = datetime.datetime.strptime(
                    show['broadcast']['time'], "%H:%M")
                ep_date = br_time-jst_dif+delay_time
                if br_time.day != ep_date.day:
                    self.weekday = self.weekday - 1 or 7
                self.start = datetime.time(
                    hour=ep_date.hour, minute=ep_date.minute)
            else:
                self.broadcast = "Unknown"
            self.episodes = 'Unkown'

            if show['episodes'] is not None:
                self.max_episodes = show['episodes']
            else:
                self.max_episodes = "?"

            self.status = show['status']
            if show['season']:
                self.season = show['season'].capitalize()+" "+str(show['year'])
            else:
                self.season = "Unknown"
            if show['studios']:
                self.studio = show['studios'][0]['name']
            else:
                self.studio = "Unknown"
            self.genre1 = show['genres'][0]['name']
            self.genre = ", ".join([x['name'] for x in show['genres']])
            self.unix_countdown = ""
            if self.status == "Currently Airing":
                self.status += " 🟢"
                start = datetime.datetime(year=show["aired"]['prop']['from']['year'], month=show["aired"]['prop']['from']['month'],
                                          day=show["aired"]['prop']['from']['day'], hour=br_time.hour, minute=br_time.minute)-jst_dif+delay_time
                self.cur_episodes = (
                    datetime.datetime.utcnow()-start).days//7+1
                offset = 0
                dels = pkl_read("delays")
                if self.name in dels:
                    offset = dels[self.name]
                    self.cur_episodes -= dels[self.name]
                del dels
                countdown = datetime.timedelta(
                    days=((self.cur_episodes)+offset)*7)+start
                self.unix_countdown = int(ti.mktime(countdown.timetuple()))
                self.unix_countdown = f"\n\nEpisode {self.cur_episodes+1}: <t:{self.unix_countdown}:R>."

                self.episodes = f"{self.cur_episodes}/{self.max_episodes}"
            elif self.status == "Finished Airing":
                self.status += " 🔴"
                self.episodes = self.max_episodes
            elif self.status == "Not yet aired":
                self.status += " 🟡"
                if self.broadcast != "Unknown":
                    self.cur_episodes = 0
                    start = datetime.datetime(year=show["aired"]['prop']['from']['year'], month=show["aired"]['prop']['from']['month'],
                                              day=show["aired"]['prop']['from']['day'], hour=br_time.hour, minute=br_time.minute)-jst_dif+delay_time
                    self.airstart=datetime.date(year=start.year,month=start.month,day=start.day)
                    countdown = start
                    self.unix_countdown = int(ti.mktime(countdown.timetuple()))
                    self.unix_countdown = f"\n\nEpisode {self.cur_episodes+1}: <t:{self.unix_countdown}:R>."

                    self.episodes = f"{self.cur_episodes}/{self.max_episodes}"

    def __str__(self):
        if self.success:
            return f"Score: {self.score}\nEpisodes: {self.episodes}\nStatus: {self.status}\nAiring: {self.airing}\nSeason: {self.season}\nBroadcast: {self.broadcast}\nGenre: {self.genre}\nStudio: {self.studio}\nURL: {self.url}{self.unix_countdown}"
        else:
            return "Anime not found."
