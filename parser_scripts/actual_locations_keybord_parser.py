from selenium.webdriver.common.by import By
from parser_scripts.parser import select_option_by_index, get_driver
from utils import kb_and_vars
from parser_scripts.parser import user_sessions

def parse_actual_locations_keybord(aucion, load_type, user_id):
    driver, session = get_driver(user_id)
    locations_arr = []

    try:
        driver.get('https://usatranscar.com/#calculator')

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

    except Exception as error:
        print(error)
    finally:
        session.close()
        del user_sessions[user_id]
        return locations_arr
