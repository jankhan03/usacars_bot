from selenium.webdriver.common.by import By
import time
from utils import kb_and_vars
from utils import prices, funcs
from parser_scripts.user_session import get_user_session, user_sessions
import re


def select_option_by_index(option_index, div_xpath, driver):
    div_select_element = driver.find_element(By.XPATH, div_xpath)
    div_select_element.click()

    auction_options = div_select_element.find_elements(By.TAG_NAME, "Option")
    auction_options[option_index].click()

    driver.find_element(By.XPATH, '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[1]').click()

    time.sleep(0.5)


def get_driver(user_id):
    session = get_user_session(user_id)

    return session.driver, session


def parse_price(load_type, auction, dispatch_site, port_of_departure, port_of_delivery, ports, auction_price, user_id,
                actual_locations):
    final_message = ""
    total = ""
    driver, session = get_driver(user_id)

    try:
        driver.get('https://usatranscar.com/#calculator')

        ul_element = driver.find_element(By.ID, "tabs-countries")
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")
        li_elements[3].click()

        driver.execute_script("window.scrollBy(0, 140);")

        time.sleep(0.7)

        input_element = driver.find_element(By.ID, kb_and_vars.load_type_dict[load_type])
        driver.execute_script("arguments[0].click();", input_element)

        # ----AUCTION SELECTION START----

        select_option_by_index(list(kb_and_vars.auction_locations_dict.keys()).index(auction),
                                     '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[2]/div[1]/div', driver)

        # ----AUCTION SELECTION END----

        # ----LOCATION SELECTION START----

        if dispatch_site not in actual_locations:
            dispatch_site = dispatch_site.replace("-", "")
            dispatch_site = re.sub(r'\s+', ' ', dispatch_site)


        select_option_by_index(actual_locations.index(dispatch_site) + 1,
                                     '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[2]/div[2]/div', driver)

        # ----LOCATION SELECTION END----

        # ----PORT DEPARTURE SELECTION START----

        select_option_by_index(ports.index(port_of_departure) + 1,
                                     '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[2]/div[3]/div', driver)

        # ----PORT DEPARTURE SELECTION END----

        # ----PORT DELIVERY SELECTION START----

        select_element = driver.find_element(By.XPATH, '//select[@id="portarrivallist-lithuania"]')

        options = select_element.find_elements(By.TAG_NAME, "option")

        if len(options) != 1:
            select_option_by_index(1, '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[2]/div[4]/div', driver)

        time.sleep(0.7)

        input_div = driver.find_element(By.XPATH, '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[3]/div/div')

        input_field = input_div.find_element(By.TAG_NAME, "input")

        input_field.send_keys(auction_price)

        temp_div = driver.find_element(By.XPATH, '//*[@id="autocalc-lithuania"]/div/div[2]/div/div[1]')
        temp_div.click()

        time.sleep(0.7)

        # ----PORT DELIVERY SELECTION END----

        # ----MAKING FINAL MESSAGE----

        land_delivery = funcs.increase_price(driver.find_element(By.XPATH,
                                                  '//*[@id="price-per-car-lithuania"]/table/tbody/tr[1]/td[2]').text, 0)

        ocean_shipping = funcs.increase_price(driver.find_element(By.XPATH,
                                                   '//*[@id="price-per-car-lithuania"]/table/tbody/tr[2]/td[2]').text, 200)

        port_service = funcs.increase_price(driver.find_element(By.XPATH,
                                           '//*[@id="price-per-car-lithuania"]/table/tbody/tr[3]/td[2]').text,
                                            prices.port_service_delta)

        # our_services = funcs.make_price_string(prices.our_services)

        delivery_klaipeda_minsk = funcs.make_price_string(prices.delivery_klaipeda_minsk)
        delivery_price = funcs.sum_prices([land_delivery, ocean_shipping, port_service, delivery_klaipeda_minsk])

        car_price = driver.find_element(By.XPATH, '//*[@id="price-per-car-lithuania"]/table/tbody/tr[7]/td[2]').text

        auction_fee = driver.find_element(By.XPATH, '//*[@id="price-per-car-lithuania"]/table/tbody/tr[8]/td[2]').text


        total = funcs.sum_prices([delivery_price,
                                  car_price, auction_fee])

        final_message = f"✅ Доставка по суше: {land_delivery}\n✅ Доставка океан: {ocean_shipping}\n✅ Доставка Клайпеда минск: {delivery_klaipeda_minsk} (цена может варьироваться от $650 до $1100 в зависимости от загруженности рынка)\n✅ Услуги порта: {port_service}, они в себя включают:\n  ↪ 30$ досмотр контейнера из-за проверок на таможне (доп платежи)\n  ↪ 15$ погрузка (доп платежи)\n  ↪ 80-120$ стоянка (из-за загрузок в порту авто, к сожалению, стоят)\n---------\n✅ Общая цена доставки: {delivery_price}\n---------\n✅ Цена транспортного средства: {car_price}\n✅ Аукционный сбор: {auction_fee}\n---------\n🟰 Итого: {total} *Без учета наших услуг\n---------\n"

        driver.quit()

    except Exception as error:
        print(error)
    finally:
        session.close()
        del user_sessions[user_id]
        return final_message, total
