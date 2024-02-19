import requests as req
from bs4 import BeautifulSoup
from datetime import datetime


def increase_price(price_string, increase_value):
    price = price_string.replace('$', '').replace(',', '')

    price_value = float(price)

    new_price_value = price_value + increase_value

    new_price_string = '${:,.2f}'.format(new_price_value)

    return new_price_string


def sum_prices(price_strings):
    total_price = 0

    for price_string in price_strings: total_price += float(price_string.replace('$', '').replace(',', ''))

    total_price_string = '${:,.2f}'.format(total_price)

    return total_price_string


def make_price_string(price): return '${:,.2f}'.format(price)


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


def _get_usd_price(data):

    result = req.get("https://myfin.by/currency/minsk")

    soup = BeautifulSoup(result.content, "html.parser")

    div_elements = soup.find_all("div", class_="course-brief-info__b")

    dollar_lst_prices = []

    dollar_to_byn_medium = float(div_elements[12].text.split(' ')[0])
    euro_to_byn_medium = float(div_elements[14].text.split(' ')[0])

    sum = 0.0

    for key in data.keys():
        if data[key] == "eur":

            tmp = (euro_to_byn_medium / dollar_to_byn_medium) * float(key)
        else:
            tmp = float(float(key) / dollar_to_byn_medium)

        sum += tmp

        dollar_lst_prices.append(make_price_string(tmp))

    return sum, dollar_lst_prices

def _get_byn_price_from_usd(data):
    pass

def get_numeric_price_from_string(price_string): float(price_string.replace('$', '').replace(',', ''))


def get_today_formatted_date(): return datetime.today().strftime("%d.%m.%Y")


def get_template(p, price):
    data = {
        f"120": "byn",
    }

    _, standard_customs_lst = _get_usd_price(data)

    price_1 = standard_customs_lst[0]

    price_2 = make_price_string(p*price)

    price_3 = make_price_string((p*price + price)*0.2)

    total = sum_prices([price_1, price_2, price_3])

    return f"✅Таможенный сбор: {price_1} по курсу НБРБ на {get_today_formatted_date()}\n✅Таможенная пошлина в размере {100*p}% от стоимости транспортного средства: {price_2}\n✅НДС 20% от суммы стоимости + таможенной таможенной пошлины: {price_3}\n🟰Итого стоимость растаможки мотоцикла составляет: {total}", total


def get_moto_customs_by_engine_capacity(engine_capacity, electro_or_no, price):

    engine_capacity = int(engine_capacity)
    price = float(price)

    if engine_capacity <= 50:
        return get_template(0.14, price)
    elif 50 < engine_capacity <= 250:
        return get_template(0.14, price)
    elif 250 < engine_capacity <= 500:
        return get_template(0.15, price)
    elif 500 < engine_capacity <= 800:
        return get_template(0.15, price)
    elif engine_capacity > 800:
        return get_template(0.10, price)
    elif electro_or_no is True:
        return get_template(0.14, price)
