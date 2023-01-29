from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import csv

BASE_URL = "https://pokemondb.net"
LAST_STORED_MON = 898

def isGreaterThan(card, n):
    return int(next(card.find("span", class_="infocard-lg-data").children).text[1:]) > n

def extractCardData(card):
    img = card.find("span", class_="infocard-lg-img").find("a").find("span")['data-src']

    data = card.find("span", class_="infocard-lg-data")
    smalls = data.find_all("small")
    number = smalls[0].text[1:]
    types = [t.text for t in smalls[1].find_all("a", class_="itype")]
    card_link = data.find("a", class_="ent-name")
    name = card_link.text

    
    dex_page = requests.get(f'{BASE_URL}{card_link["href"]}')
    dex_soup = BeautifulSoup(dex_page.content, "html.parser")
    hp = dex_soup.find("th", text="HP").parent.find("td").text
    attack = dex_soup.find("th", text="Attack").parent.find("td").text
    defense = dex_soup.find("th", text="Defense").parent.find("td").text
    sp_attack = dex_soup.find("th", text="Sp. Atk").parent.find("td").text
    sp_def = dex_soup.find("th", text="Sp. Def").parent.find("td").text
    speed = dex_soup.find("th", text="Speed").parent.find("td").text
    total = dex_soup.find("th", text="Total").parent.find("td").text

    row = [number, img, name, hp, attack, defense, sp_attack, sp_def, speed, total]
    row.extend(types)
    return row



page = requests.get(f'{BASE_URL}/pokedex/national')
soup = BeautifulSoup(page.content, "html.parser")

infocards = soup.find_all("div", class_="infocard")
filtered_infocards = (card for card in infocards if isGreaterThan(card, LAST_STORED_MON))

with ThreadPoolExecutor(max_workers = 100) as executor:
    results = executor.map(extractCardData, filtered_infocards)

with open("output.csv", 'w', newline='') as file:
    writer = csv.writer(file).writerows(results)



