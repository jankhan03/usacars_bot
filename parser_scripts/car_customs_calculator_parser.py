import time

from utils import text
from selenium.webdriver.common.by import By
from parser_scripts.parser import get_driver
from utils.funcs import _get_usd_price, make_price_string, get_today_formatted_date
from parser_scripts.parser import user_sessions

def parse_car_customs_price(car_age, car_price, engine_capacity, lfdp, electro_or_no, user_id):
    final_message = ""
    sum_dollars = ""
    driver, session = get_driver(user_id)

    electro_or_no = True if electro_or_no == text.lfdp_yes else False

    try:
        driver.get("https://avtoportal.by/rastamozhka-avto-v-belarusi-kalkulyator/")

        driver.execute_script("window.scrollBy(0, 3963);")

        select_element = driver.find_element(By.XPATH, '//select[@id="calc_age"]')

        options = select_element.find_elements(By.TAG_NAME, 'option')

        if int(car_age) < 3:
            options[0].click()
            driver.execute_script("window.scrollBy(3963, 50);")

            div_input = driver.find_element(By.XPATH, '//*[@id="abId0.5343256928223925"]')
            input_field = div_input.find_element(By.TAG_NAME, 'input')
            input_field.send_keys(car_price)

        elif 3 <= int(car_age) < 5:
            options[1].click()
        elif 5 <= int(car_age) < 7:
            options[2].click()
        else:
            options[3].click()

        div_input_capacity = driver.find_element(By.XPATH, '//*[@id="abId0.9388309808731146"]')
        input_field_capacity = div_input_capacity.find_element(By.TAG_NAME, 'input')
        input_field_capacity.send_keys(engine_capacity)

        if lfdp == text.lfdp_yes:
            checkbox_label = driver.find_element(By.XPATH, '//*[@id="discount"]/div/label')

            checkbox_label.click()

        calculate_button = driver.find_element(By.XPATH, '//input[@id="calc_btn"]')

        calculate_button.click()

        driver.execute_script("window.scrollBy(4013, 130);")

        price_1 = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[2]/div[2]/main/article/div[2]/div[8]/div/div/div[6]/div[1]/span[1]').text
        price_2 = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[2]/div[2]/main/article/div[2]/div[8]/div/div/div[6]/div[1]/span[2]').text
        price_3 = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[2]/div[2]/main/article/div[2]/div[8]/div/div/div[6]/div[1]/span[3]').text

        # sum_dollars = _get_usd_price(float(price_1), "eur") if not electro_or_no else 0.0 + \
        #     _get_usd_price(float(price_2), "byn") + _get_usd_price(price_3, "byn") if not electro_or_no else 0.0

        if electro_or_no:
            data = {
                f"{float(price_2)}": "byn",
                f"{float(price_3)}": "byn",
            }
        else:
            data = {
                f"{float(price_1)}": "eur",
                f"{float(price_2)}": "byn",
                f"{float(price_3)}": "byn",
            }

        sum_dollars, sep_dol_prs = _get_usd_price(data)

        customs_duty = f"✅ Таможенная пошлина: {price_1} евро ({sep_dol_prs[0]})"
        customs_duty_2 = f"✅ Таможенный сбор: {price_3} бел. руб. ({sep_dol_prs[2] if not electro_or_no else sep_dol_prs[1]})"

        final_message = f"🛂 Затраты на растаможку:\n\n{customs_duty if not electro_or_no else ''}\n✅ Утилизационный сбор: {price_2} бел.руб. ({sep_dol_prs[1] if not electro_or_no else sep_dol_prs[0]})\n" \
                        f"{customs_duty_2}\n---------\n🟰 Итого: " \
                        f"{make_price_string(sum_dollars)} по курсу НБРБ на {get_today_formatted_date()}\n---------\n"

    except Exception as error:
        print(error)
    finally:
        session.close()
        del user_sessions[user_id]
        return final_message, make_price_string(sum_dollars)

# print(parse_car_customs_price(88, 10000, 2000, text.lfdp_yes))