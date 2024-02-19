from selenium.webdriver.common.by import By
from parser_scripts.parser import select_option_by_index, get_driver
from utils import kb_and_vars
from parser_scripts.parser import user_sessions

def parse_ports_departure_and_delivery(aucion, dispatch_site, load_type, user_id, actual_locations) -> []:
    driver, session = get_driver(user_id)
    ports_departure = []
    ports_delivery = []

    try:
        driver.get('https://usatranscar.com/#calculator')

        ul_element = driver.find_element(By.ID, "tabs-countries")
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")
        li_elements[3].click()

        driver.execute_script("window.scrollBy(0, 110);")

        input_element = driver.find_element(By.ID, kb_and_vars.load_type_dict[load_type])
        driver.execute_script("arguments[0].click();", input_element)

        # ----AUCTION SELECTION START----

        select_option_by_index(list(kb_and_vars.auction_locations_dict.keys()).index(aucion),
                               '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[2]/div[1]/div', driver)

        # ----AUCTION SELECTION END----

        # ----LOCATION SELECTION START----

        select_option_by_index(actual_locations.index(dispatch_site) + 1,
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
        return ports_departure, ports_delivery
