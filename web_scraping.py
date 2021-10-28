import requests
from bs4 import BeautifulSoup
import re
team = "DAL"
season = "2020"
url = "https://www.basketball-reference.com/teams/" + team + "/" + season + ".html"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")


first_table = soup.find_all("p")
tags = [attribute.getText().strip() for attribute in first_table]
records = re.findall(r"(\d+)",tags[2])
n_win = records[0]
n_loss = records[1]
conf_ranking = records[2]
coach_regex = re.findall(r"([A-Z][a-z]+\s[A-Z][a-z]+)",tags[3][7:])
coach = coach_regex[0]
points = re.findall(r"(\d+\.\d+)",tags[5])
ppg = points[0]
opponent_ppg = points[-1]
paces = re.findall(r"(\d+\.\d+)",tags[6])[-1]
pace = paces[-1]
rtgs = re.findall(r"(\d+\.\d+)",tags[7])
off_rtg = rtgs[0]
def_rtg = rtgs[1]
expected = re.findall(r"(\d+)",tags[8])
expected_win = expected[0]
expected_loss = expected[1]
expected_overall_ranking = expected[2]
odds = re.findall(r"(\+\d+)",tags[9])
preseason_odds = odds[0]
attendances = re.findall(r"(\d+)",tags[10])
attendance = attendances[0]
try:
    playoffs = tags[11].split("(Series Stats)")[-2]
except:
    playoffs = "Not in playoffs"
result = [team, season, n_win, n_loss, conf_ranking, coach, ppg, opponent_ppg, pace, off_rtg, def_rtg, expected_win,
          expected_loss, expected_overall_ranking, preseason_odds, attendance, playoffs]

"""
for index,i in enumerate(tags):
    print(index, "+", i)"""




second_table = soup.find_all("table")[0].get_text()
pattern = r"(\d+)(\D+)(PF|C|PG|SF|SG)(\d+\-\d+)([A-Za-z]+) (\d+), (\d+)([a-z]+)(\d+|R)"
st = re.findall(pattern,second_table)
roster = []
for player in st:
    player = list(player)
    player.append(player[3][:-3])
    player.append(player[3][-3:])
    player.pop(3)
    player.append(team)
    player.append(season)
    roster.append(player)


nr_of_players = len(roster)
team = [team for i in range(nr_of_players)]
season = [season for i in range(nr_of_players)]
name = [element.get_text() for element in soup.find_all("td", {"data-stat":"player"})][:nr_of_players]
age = [element.get_text() for element in soup.find_all("td", {"data-stat":"age"})][:nr_of_players]
g = [element.get_text() for element in soup.find_all("td", {"data-stat":"g"})][:nr_of_players]
gs = [element.get_text() for element in soup.find_all("td", {"data-stat":"gs"})][:nr_of_players]
mp_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"mp_per_g"})][:nr_of_players]
fg_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"fg_per_g"})][:nr_of_players]
fga_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"fga_per_g"})][:nr_of_players]
fg_pct = [element.get_text() for element in soup.find_all("td", {"data-stat":"fg_pct"})][:nr_of_players]
fg3_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"fg3_per_g"})][:nr_of_players]
fg3a_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"fg3a_per_g"})][:nr_of_players]
fg3_pct = [element.get_text() for element in soup.find_all("td", {"data-stat":"fg3_pct"})][:nr_of_players]
fg2_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"fg2_per_g"})][:nr_of_players]
fg2a_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"fg2a_per_g"})][:nr_of_players]
fg2_pct = [element.get_text() for element in soup.find_all("td", {"data-stat":"fg2_pct"})][:nr_of_players]
ft_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"ft_per_g"})][:nr_of_players]
fta_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"fta_per_g"})][:nr_of_players]
ft_pct = [element.get_text() for element in soup.find_all("td", {"data-stat":"ft_pct"})][:nr_of_players]
orb_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"orb_per_g"})][:nr_of_players]
drb_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"drb_per_g"})][:nr_of_players]
trb_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"trb_per_g"})][:nr_of_players]
ast_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"ast_per_g"})][:nr_of_players]
stl_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"stl_per_g"})][:nr_of_players]
blk_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"blk_per_g"})][:nr_of_players]
tov_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"tov_per_g"})][:nr_of_players]
pf_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"pf_per_g"})][:nr_of_players]
pts_per_g = [element.get_text() for element in soup.find_all("td", {"data-stat":"pts_per_g"})][:nr_of_players]


print(season, "\n", team, "\n",name,"\n",age,"\n",g,"\n",gs,"\n",mp_per_g,"\n",fg_per_g,"\n",fga_per_g,"\n",fg_pct,"\n",fg3_pct,"\n",
      fg3_per_g,"\n",fg3a_per_g,"\n",fg2_per_g,"\n",fg2a_per_g,"\n",fg2_pct,"\n",ft_pct,"\n",ft_per_g,"\n",
      fta_per_g,"\n", orb_per_g, "\n", drb_per_g, "\n", trb_per_g, "\n", ast_per_g, "\n", stl_per_g, "\n",
      stl_per_g, "\n", blk_per_g, "\n", tov_per_g, "\n", pf_per_g, "\n", pts_per_g)



