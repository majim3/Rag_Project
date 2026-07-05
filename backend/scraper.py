

from time import sleep
import json

import requests
from bs4 import BeautifulSoup

url = "https://duunitori.fi/tyopaikat?haku=it"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
contents = soup.find_all("a", class_="job-box__hover gtm-search-result")




info_list = []

for content in contents:
   


    link_raw = content.get("href")
    company = content.get("data-company")
    link = f"https://duunitori.fi{link_raw}"
    name = content.get_text().strip()

    info = {
        "link": link,
        "company": company,
        "name": name
    }

    info_list.append(info)

description_data_list = []  
   
for info in info_list:

    description_data = requests.get(info["link"])

    soup = BeautifulSoup(description_data.text, "html.parser")

    decpription_soup = soup.find("div", class_="gtm-apply-clicks description description--jobentry")

    description_text = decpription_soup.get_text() if decpription_soup else "No description found."

    description_data = {
        "link": info["link"],
        "company": info["company"],
        "name": info["name"],
        "description": description_text
    }
    description_data_list.append(description_data)


    sleep(3) 

json_data = json.dumps(description_data_list, ensure_ascii=False, indent=4)
print(json_data)




   