import time

from selenium.webdriver.common.by import By
from parser_scripts.parser import select_option_by_index, get_driver
from utils import kb_and_vars
from parser_scripts.parser import user_sessions
import re
from parser_scripts.info_from_link_parser import find_most_similar

def parse_actual_and_ports(aucion, load_type, dispatch_site, user_id):
    driver, session = get_driver(user_id)
    locations_arr = []
    ports_departure = []
    ports_delivery = []

    try:
        driver.get('https://usatranscar.com/#calculator')
        time.sleep(2)

        ul_element = driver.find_element(By.ID, "tabs-countries")
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")
        li_elements[3].click()

        driver.execute_script("window.scrollBy(0, 110);")

        input_element = driver.find_element(By.ID, kb_and_vars.load_type_dict[load_type])
        driver.execute_script("arguments[0].click();", input_element)

        select_option_by_index(list(kb_and_vars.auction_locations_dict.keys()).index(aucion),
                               '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[2]/div[1]/div', driver)

        locations = driver.find_element(By.XPATH, '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[2]/div[2]/div')

        locations_options = locations.find_elements(By.TAG_NAME, "option")

        locations_arr = [location_option.text for location_option in locations_options]

        # ----LOCATION SELECTION START----

        if dispatch_site not in locations_arr:
            dispatch_site = find_most_similar(dispatch_site, locations_arr)

        select_option_by_index(locations_arr.index(dispatch_site) + 1,
                               '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[2]/div[2]/div', driver)

        # ----LOCATION SELECTION END----

        # ----PORT DEPARTURE SELECTION START----

        select_element = driver.find_element(By.XPATH, '//select[@id="portloadinglist-lithuania"]')

        options = select_element.find_elements(By.TAG_NAME, "option")

        for option in options:
            ports_departure.append(option.text)

        if '' in ports_departure:
            ports_departure.remove('')

        if 'Port of departure' in ports_departure:
            ports_departure.remove('Port of departure')
        # ----PORT DEPARTURE SELECTION END----

        select_element_delivery = driver.find_element(By.XPATH, '//select[@id="portarrivallist-lithuania"]')
        options_delivery = select_element_delivery.find_elements(By.TAG_NAME, "option")

        for option in options_delivery:
            ports_delivery.append(option.text)

        if "Port of delivery" in ports_delivery:
            ports_delivery.remove("Port of delivery")

    except Exception as error:
        print(error)
    finally:
        session.close()
        del user_sessions[user_id]
        return ports_departure, ports_delivery, locations_arr


# ports_departure, ports_delivery, locations_arr = parse_actual_and_ports("Copart", "Sedan", "CA ANTELOPE", 0)
#
# print(ports_departure, ports_delivery, locations_arr)