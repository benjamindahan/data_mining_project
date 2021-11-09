import grequests
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import conf as c
import time

start_time = time.time()
def double_list(list_1,list_2):
    return [x for pair in zip(list_1,list_2) for x in pair]

URL_1 = "https://www.basketball-reference.com/leagues/NBA_"
URL_2 = "_games-"
URL_3 = ".html"

month = []
day = []
year = []
box_score = []
visitor_team = []
home_team = []

MONTHS = ["october", "november", "december", "january", "february", "march", "may", "june"]
seasons = [str(year) for year in range(2008, 2020)]

list_of_urls_scores = []
for y in seasons:
    for m in MONTHS:
        url = URL_1 + y + URL_2 + m + URL_3
        list_of_urls_scores.append(url)

rs = (grequests.get(url) for url in list_of_urls_scores)
responses = grequests.map(rs, size=c.BATCHES)
for url, response in zip(list_of_urls_scores, responses):
    if response is not None:
        # Creating the soup object
        soup = BeautifulSoup(response.text, "html.parser")

        url_page = soup.find_all("a")
        url_box_score = [url.get("href").strip() for url in url_page]
        url_buenos = []
        date = []
        box_score_aux = []
        home = []
        visitor = []
        teams = []
        for url in url_box_score:
            if "boxscores" in url:
                url_buenos.append(url)
            elif "teams" in url:
                teams.append(url)

        for i,team in enumerate(teams[2:]):
            if i % 2 != 0:
                visitor.append(team)
            else:
                home.append(team)

        for i,j in enumerate(url_buenos[1:]):
            if i % 2 == 0:
                date.append(j)
            else:
                box_score_aux.append("https://www.basketball-reference.com" + j)

        box_score += box_score_aux[:-1]
        box_score_aux = box_score_aux[:-1]
        home = home[0:len(box_score_aux)]
        visitor = visitor[0:len(box_score_aux)]

        for h,v in zip(home,visitor):
            if len(h) > 17:
                h = h[7:-10]
                if len(h) == 3:
                    visitor_team.append(h)
            if len(v) > 17:
                v = v[7:-10]
                if len(v) == 3:
                    home_team.append(v)



        for url in date:
            try:
                matches = re.findall(r'(month=)(\d+)(&)(day=)(\d+)(&)(year=)(\d+)',url)[0]
                if len(matches) == 8:
                    month.append(matches[1])
                    day.append(matches[4])
                    year.append(matches[-1])
            except:
                pass

print("DAY: ",len(day))
print("BS: ", len(box_score))
print("HT: ", len(home_team))
assert len(day) == len(month)
assert len(day) == len(year)
assert len(day) == len(box_score)
assert len(day) == len(home_team)
assert len(day) == len(visitor_team)

day_doubles = double_list(day,day)
month_doubles = double_list(month,month)
year_doubles = double_list(year,year)
home_team_doubles = double_list(home_team,visitor_team)
visitor_team_doubles = double_list(visitor_team,home_team)
box_score_doubles = double_list(box_score,box_score)
home_team_boolean = [1,0]*len(day)

dictionary_scores = {"day": day_doubles, "month": month_doubles, "year": year_doubles, "home_team": home_team_boolean,
                         "team": home_team_doubles, "opponent": visitor_team_doubles, "url": box_score_doubles}

df = pd.DataFrame(dictionary_scores)
df.to_csv("df.csv")
end_time = time.time()
print(end_time-start_time, c.BATCHES)