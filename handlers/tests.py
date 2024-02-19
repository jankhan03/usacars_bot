import requests as req
from bs4 import BeautifulSoup

result = req.get("https://myfin.by/currency/minsk")

soup = BeautifulSoup(result.content, "html.parser_scripts")

div_elements = soup.find_all("div", class_="course-brief-info__b")

dollar_to_byn_medium = float((float(div_elements[3].text) + float(div_elements[4].text)) / 2)
euro_to_byn_medium = float((float(div_elements[6].text) + float(div_elements[7].text)) / 2)

print(dollar_to_byn_medium, euro_to_byn_medium)
