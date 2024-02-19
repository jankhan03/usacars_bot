from selenium.webdriver.common.by import By
from parser_scripts.parser import select_option_by_index, get_driver
from utils import kb_and_vars
from parser_scripts.parser import user_sessions
import time
import re
import requests as req
from bs4 import BeautifulSoup
import difflib

def find_most_similar(target, list_of_strings):
    similarity_ratios = [(difflib.SequenceMatcher(None, target, s).ratio(), s) for s in list_of_strings]
    similarity_ratios.sort(reverse=True)
    return similarity_ratios[0][1] if similarity_ratios else None


def parse_from_link_bs4(link):
    car_info = {}

    try:
        if isinstance(link, int):
            car_info["auction"] = "IAAI"
            lot_number = str(link)
            carcheck_find_url = f"https://carcheck.by/a2/auto.php?auction=1&vin={lot_number}"
        elif "https://www.copart.com/lot/" in link or "https://www.copart.com/ru/lot/" in link or\
                "https://www.copart.de/lot/" in link:
            car_info["auction"] = "Copart"
            found_digits = re.search(r'lot/(\d+)', link)
            lot_number = found_digits.group(1)
            carcheck_find_url = f"https://carcheck.by/auto/{lot_number}"
        else:
            return None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/58.0.3029.110 Safari/537.3'
        }

        result = req.get(carcheck_find_url, headers=headers)
        soup = BeautifulSoup(result.content, "html.parser")

        engine_capacity_element = soup.select_one("body > div.block_hide > div.content > div:nth-child(2) > "
                                                  "div.one_slyd > div:nth-child(3) > div > div.one_tab_left > "
                                                  "div:nth-child(1) > div.t_coll > div:nth-child(5) > span")
        if engine_capacity_element:
            engine_capacity_string = engine_capacity_element.text
            if "L" in engine_capacity_string and "ELECTRIC" not in engine_capacity_string:
                car_info["engine_capacity"] = engine_capacity_string[:engine_capacity_string.find("L")]
            else:
                car_info["engine_capacity"] = engine_capacity_string

        car_info["location"] = ' '.join(soup.select_one("body > div.block_hide > div.content > div:nth-child(2) > "
                                                       "div.one_slyd > div:nth-child(3) > div > div.one_tab_left >"
                                                       " div:nth-child(1) > div.t_coll > div:nth-child(6) > "
                                                       "span").text.replace("-", "").split())

        car_info["car_name"] = soup.select_one("body > div.block_hide > div.content > div:nth-child(2) > div.one_slyd >"
                                               " div:nth-child(1) > div.one_tit > div > span:nth-child(1)").text

        car_info["car_age"] = soup.select_one("body > div.block_hide > div.content > div:nth-child(2) > div.one_slyd > "
                                              "div:nth-child(3) > div > div.one_tab_left > div:nth-child(1) > "
                                              "div.t_coll > div:nth-child(1) > span").text

        return car_info
    except Exception as error:
        print(error)
        return car_info

lot_number = 37602170
# print(parse_from_link_bs4("https://www.copart.com/lot/77927903/salvage-2020-alfa-romeo-stelvio-va-hampton"))
# print(parse_from_link_bs4(lot_number))
# 73898323
# print(parse_from_link_bs4("https://www.copart.com/lot/73898323"))
