import requests
from bs4 import BeautifulSoup

url = "https://www.basketball-reference.com/teams/MIA/2021.html"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

first_table = soup.find_all("p")
print(first_table)
