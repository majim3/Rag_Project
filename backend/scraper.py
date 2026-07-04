import requests
from bs4 import BeautifulSoup

url = "https://duunitori.fi/tyopaikat?haku=it"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

Jobs = soup.find_all("div", class_="grid grid--middle job-box job-box--lg")

contents = soup.find_all("a", class_="job-box__hover gtm-search-result")
print(f"Data: {Jobs.__len__()}")
print(f"Content: {contents.__len__()}")


for job in Jobs:
    content = job.find("div", class_="job-box__content")
   
    
    name = content.find("h3", class_="job-box__title").text.strip()
    print(f"name: {name}")
    
    
    