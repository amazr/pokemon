from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import csv

BASE_URL = "https://pokemondb.net"
LAST_STORED_MON = 0

def isGreaterThan(card, n):
    return int(next(card.find("span", class_="infocard-lg-data").children).text[1:]) > n

def getStat(source, stat_str):
    return [tbody.parent.find("td").text for tbody in source.find_all("th", text=stat_str)]

def extractCardData(card):
    data = card.find("span", class_="infocard-lg-data")
    dex_page = requests.get(f'{BASE_URL}{data.find("a", class_="ent-name")["href"]}')
    dex_soup = BeautifulSoup(dex_page.content, "html.parser")

    return {
        "num": data.find("small").text[1:],
        "img_urls": [url.find("img")['src'] for url in dex_soup.find_all("picture")[1:]],
        "names": [name.text for name in dex_soup.find("div", class_="sv-tabs-tab-list") if name != '\n'],
        "hp": getStat(dex_soup, "HP"),
        "attack": getStat(dex_soup, "Attack"),
        "defense": getStat(dex_soup, "Defense"),
        "sp_atk": getStat(dex_soup, "Sp. Atk"),
        "sp_def": getStat(dex_soup, "Sp. Def"),
        "speed": getStat(dex_soup, "Speed"),
        "total": getStat(dex_soup, "Total"),
        "types": [list(map(lambda x: x.text, tbody.parent.find_all("a"))) for tbody in dex_soup.find_all("th", text="Type") if len(tbody.parent.find_all("a")) > 0]
    }

def unpackAndWriteRow(writer, data):
    for i in range(0, len(data['img_urls'])):
        row = [data['num']]
        row.append(data['img_urls'][i])
        row.append(data['names'][i])
        row.append(data['hp'][i])
        row.append(data['attack'][i])
        row.append(data['defense'][i])
        row.append(data['sp_atk'][i])
        row.append(data['sp_def'][i])
        row.append(data['speed'][i])
        row.append(data['total'][i])
        row.extend(data['types'][i])
        writer.writerow(row)


page = requests.get(f'{BASE_URL}/pokedex/national')
soup = BeautifulSoup(page.content, "html.parser")

infocards = soup.find_all("div", class_="infocard")
filtered_infocards = (card for card in infocards if isGreaterThan(card, LAST_STORED_MON))

with ThreadPoolExecutor(max_workers = 1000) as executor:
    results = executor.map(extractCardData, filtered_infocards)

with open("output.csv", 'w', newline='', encoding="utf-8") as file:
    for result in results:
        unpackAndWriteRow(csv.writer(file), result)



