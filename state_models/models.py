from aiogram.dispatcher.filters.state import StatesGroup, State


class DeliveryPriceCalculator(StatesGroup):
    load_type = State()
    auction = State()
    location = State()
    port_of_departure = State()
    port_of_delivery = State()
    auction_price = State()
    go_to_manager = State()
    final_stage = State()
    go_to_manager_another_load_type = State()


class CarCustomsCalculator(StatesGroup):
    car_age = State()
    electro_or_no = State()
    motorcycle = State()
    car_price = State()
    engine_capacity = State()
    lfdp_choice = State()
    go_to_manager = State()
    final_stage = State()


class ContactInfo(StatesGroup):
    tel_number = State()
    message = State()


class BothCalculator(StatesGroup):
    load_type = State()
    car_age = State()
    electro_or_no = State()
    motorcycle = State()
    engine_capacity = State()
    lfdp_choice = State()
    auction = State()
    location = State()
    port_of_departure = State()
    port_of_delivery = State()
    auction_price = State()
    go_to_manager = State()
    final_stage = State()
    go_to_manager_or_no_another_load_type = State()


class BothCalculatorByLink(StatesGroup):
    load_type = State()
    auction_price = State()
    link_stage = State()
    go_to_manager = State()
    go_to_manager_or_no_another_load_type = State()
    final_stage = State()
    port_of_departure = State()
    port_of_delivery = State()
    lfdp_choice = State()
    no_car_capacity_phase_1 = State()
    no_car_capacity_phase_2 = State()