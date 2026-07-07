import os
from time import sleep
import json
import requests
from bs4 import BeautifulSoup


url = "https://duunitori.fi/tyopaikat?haku=it"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
contents = soup.find_all("a", class_="job-box__hover gtm-search-result")

def get_data_from_url():
    info_list = []
    print("Getting data from URL...")

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
    return info_list

def get_description_data(info_list):
    description_data_list = [] 
    print("Getting description data from each link...")

    
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


        sleep(2) 
    print("Description data retrieval complete.")

    __location__ = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(__location__, "description_data.json"), "w", encoding="utf-8") as f:
        json.dump(description_data_list, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":  
    info_list = get_data_from_url()
    get_description_data(info_list)







   