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
    
   
print(f"info_list: {info_list}")
    