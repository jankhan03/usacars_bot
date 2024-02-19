from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from utils import kb_and_vars, text
from aiogram.dispatcher import FSMContext
from handlers.bot_manager import dp, bot
from state_models.models import BothCalculatorByLink, ContactInfo
from parser_scripts.select_options_parser import parse_ports_departure_and_delivery
import asyncio
from handlers.car_customs_calculator_handler import precalculating_car_customs
from utils import funcs
from datetime import datetime
from utils.funcs import get_moto_customs_by_engine_capacity
from handlers.price_calculator_handler import process_price_parsing
from config import admin_id
from parser_scripts.info_from_link_parser import parse_from_link_bs4, find_most_similar
from parser_scripts import actual_locations_keybord_parser
from parser_scripts.actual_locations_and_ports_parser import parse_actual_and_ports


def convert_to_int_value(value):
    try:
        return int(value)
    except ValueError:
        return None

@dp.message_handler(state=BothCalculatorByLink.load_type)
async def answer_load_type_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return
    elif answer == text.another or answer == text.load_types_dict[text.pickup]:
        await state.finish()
        await BothCalculatorByLink.go_to_manager.set()
        await message.answer("Уточните информацию у менеджера", reply_markup=kb_and_vars.go_to_manager_menue)
        await BothCalculatorByLink.go_to_manager_or_no_another_load_type.set()
        return

    elif answer not in text.load_types_dict.values():
        await message.answer("Выбран неверный load type, попробуйте еще раз", reply_markup=kb_and_vars.load_type_menue)
        await BothCalculatorByLink.load_type.set()
        return

    async with state.proxy() as data:
        data["answer_load_type"] = answer
        data["motorcycle"] = text.lfdp_yes if funcs.get_key(text.load_types_dict, data["answer_load_type"]) == text.motorcycle else text.lfdp_no

    await message.answer("💰 Введите цену транспортного средства в долларах США (например: 10000)",
                         reply_markup=kb_and_vars.exit_kb)

    await BothCalculatorByLink.auction_price.set()

@dp.message_handler(state=BothCalculatorByLink.auction_price)
async def answer_load_type_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif not answer.isdigit():
        await message.answer("Введите число, а не строку", reply_markup=kb_and_vars.exit_kb)
        await BothCalculatorByLink.auction_price.set()
        return

    async with state.proxy() as data:
        data["auction_price"] = answer

    await message.answer("🔗 Скиньте ссылку лота на аукционе COPART. Для IAAI скиньте НОМЕР ЛОТА:", reply_markup=kb_and_vars.exit_kb)
    await BothCalculatorByLink.link_stage.set()


@dp.message_handler(state=BothCalculatorByLink.link_stage)
async def answer_load_type_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif "https://www.copart.com/lot/" not in answer:
        answer = convert_to_int_value(answer)
        if not answer:
            await message.answer("Неверный формат данных, попробуйте еще раз:", reply_markup=kb_and_vars.exit_kb)
            await BothCalculatorByLink.auction_price.set()
            return

    async with state.proxy() as data:
        data["link"] = answer

    await message.answer("⏳ Идет сбор информации с аукциона, ожидайте.", reply_markup=ReplyKeyboardRemove())

    car_info = parse_from_link_bs4(answer)

    if len(car_info) != 5:
        await message.answer("Произошла ошибка, попробуйте еще раз", reply_markup=kb_and_vars.exit_kb)
        await message.answer("🔗 Скиньте ссылку лота на аукционе COPART. Для IAAI скиньте НОМЕР ЛОТА:",
                             reply_markup=kb_and_vars.exit_kb) # reply_markup=ReplyKeyboardRemove()
        await BothCalculatorByLink.link_stage.set()


    if not car_info:
        await message.answer("⛔️ Неверная ссылка или номер лота, попробуйте еще раз...", reply_markup=kb_and_vars.exit_kb)
        await message.answer("🔗 Скиньте ссылку лота на аукционе COPART. Для IAAI скиньте НОМЕР ЛОТА:",
                             reply_markup=kb_and_vars.exit_kb) # reply_markup=ReplyKeyboardRemove()
        await BothCalculatorByLink.link_stage.set()

    async with state.proxy() as data:
        data["answer_auction"] = car_info["auction"]
        data["answer_location"] = car_info["location"]
        today_year = int(datetime.today().year)
        data["car_age"] = today_year - int(car_info["car_age"])
        data["electro_or_no"] = text.lfdp_yes if "ELECTRIC" in car_info["engine_capacity"] else text.lfdp_no

        if car_info["engine_capacity"]:
            data["engine_capacity"] = float(car_info["engine_capacity"]) * 1000 if\
                                    data["electro_or_no"] == text.lfdp_no else "2000"

        data["ports"], data["ports_delivery"], locations = parse_actual_and_ports(data["answer_auction"],
                                                                                  funcs.get_key(text.load_types_dict,
                                                                                                data["answer_load_type"]),
                                                                                  data["answer_location"],
                                                                                  message.chat.id)
        if not locations:
            await message.answer("Произошла ошибка, попробуйте еще раз", reply_markup=kb_and_vars.exit_kb)
            await message.answer("🔗 Скиньте ссылку лота на аукционе COPART. Для IAAI скиньте НОМЕР ЛОТА:",
                                 reply_markup=kb_and_vars.exit_kb)  # reply_markup=ReplyKeyboardRemove()
            await BothCalculatorByLink.link_stage.set()

        if data["answer_location"] not in locations:
            data["answer_location"] = find_most_similar(data["answer_location"], locations)

        locations.pop(0)
        data["actual_locations"] = locations

    if not car_info["engine_capacity"]:
        await BothCalculatorByLink.no_car_capacity_phase_1.set()
        await message.answer("❓ Не было обнаружено объема двигателя, выберете действие...",
                             reply_markup=kb_and_vars.no_car_capacity_menu)

    else:
        await BothCalculatorByLink.port_of_departure.set()

        await message.answer("🚢 Выберете порт отправки:", reply_markup=kb_and_vars.get_keybord(data["ports"]))


@dp.message_handler(state=BothCalculatorByLink.no_car_capacity_phase_1)
async def answer_no_car_phase_1(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    if answer == text.no_car_capacity_type_capacity_text:
        await BothCalculatorByLink.no_car_capacity_phase_2.set()
        await message.answer("⛽️ Введите объем двигателя в см. куб. (2 литра = 2000 см. куб.)",
                             reply_markup=kb_and_vars.exit_kb)
    elif answer == text.no_car_capacity_electro_text:
        async with state.proxy() as data:
            data["electro_or_no"] = text.lfdp_yes
            await BothCalculatorByLink.port_of_departure.set()

            await message.answer("🚢 Выберете порт отправки:", reply_markup=kb_and_vars.get_keybord(data["ports"]))


@dp.message_handler(state=BothCalculatorByLink.no_car_capacity_phase_2)
async def answer_no_car_phase_2(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return
    elif not answer.isdigit():
        await BothCalculatorByLink.no_car_capacity_phase_1.set()
        await message.answer("Введите число, а не строку:", reply_markup=kb_and_vars.exit_kb)
        return

    elif int(answer) <= 0:
        await BothCalculatorByLink.no_car_capacity_phase_1.set()
        await message.answer("Введите число больше нуля", reply_markup=kb_and_vars.exit_kb)
        return

    async with state.proxy() as data:
        data["engine_capacity"] = answer

    await BothCalculatorByLink.port_of_departure.set()

    await message.answer("🚢 Выберете порт отправки:", reply_markup=kb_and_vars.get_keybord(data["ports"]))



@dp.message_handler(state=BothCalculatorByLink.port_of_departure)
async def answer_port_of_departure_two(message: types.Message, state: FSMContext):
    answer = message.text

    async with state.proxy() as data:
        if answer == text.exit_text:
            await state.finish()
            await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
            return
        elif answer not in data["ports"]:
            await message.answer("Выбран неверный порт отправки, попробуйте еще раз",
                                 reply_markup=kb_and_vars.get_keybord(data["ports"]))
            await BothCalculatorByLink.port_of_departure.set()
            return

    async with state.proxy() as data:
        data["answer_port_of_departure"] = answer
        await message.answer("🚢 Выберете порт прибытия:", reply_markup=kb_and_vars.get_keybord(data["ports_delivery"]))

    await BothCalculatorByLink.port_of_delivery.set()


@dp.message_handler(state=BothCalculatorByLink.port_of_delivery)
async def answer_port_of_delivery_two(message: types.Message, state: FSMContext):
    answer = message.text

    async with state.proxy() as data:
        if answer == text.exit_text:
            await state.finish()
            await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
            return
        elif answer not in kb_and_vars.ports_of_delivery:
            if len(data["answer_port_of_departure"]) != 0:
                await message.answer("Выбран неверный порт прибытия, попробуйте еще раз",
                                     reply_markup=kb_and_vars.ports_of_delivery_menue)
                await BothCalculatorByLink.port_of_delivery.set()
                return
            else:
                pass

    async with state.proxy() as data:
        data["answer_port_of_delivery"] = answer

    await BothCalculatorByLink.lfdp_choice.set()
    await message.answer("📄 Льготная таможня под 1️⃣4️⃣0️⃣ указ?", reply_markup=kb_and_vars.lfdp_choice_menue)


@dp.message_handler(state=BothCalculatorByLink.lfdp_choice)
async def answer_lfdp_choice_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif answer not in [text.lfdp_yes, text.lfdp_no]:
        await BothCalculatorByLink.lfdp_choice.set()
        await message.answer("Выбран неверный вариант, попробуйте еще раз:", reply_markup=kb_and_vars.lfdp_choice_menue)
        return

    async with state.proxy() as data:
        data["lfdp_choice"] = answer

    await message.answer("⏳ Ваша цена рассчитывается, ожидайте.", reply_markup=ReplyKeyboardRemove())

    async with state.proxy() as data:
        task1 = process_price_parsing(
            message.chat.id,
            funcs.get_key(text.load_types_dict, data["answer_load_type"]),
            data["answer_auction"],
            data["answer_location"],
            data["answer_port_of_departure"],
            data["answer_port_of_delivery"],
            data["ports"],
            data["auction_price"],
            data["actual_locations"],
            is_both_parsers=True, state=state)

        if data["motorcycle"] == text.lfdp_no:
            task2 = precalculating_car_customs(
                data["car_age"],
                data["auction_price"],
                data["engine_capacity"],
                data["lfdp_choice"],
                message.chat.id,
                data["electro_or_no"],
                is_both_parsers=True, state=state)

            result1, result2 = await asyncio.gather(*[task1, task2])
            if not result1 or not result2:
                await state.finish()
                await bot.send_message(message.chat.id, "Произошла ошибка, повторите попытку позже",
                                       reply_markup=kb_and_vars.main_menu)
                return
            message1, sum1 = result1
            message2, sum2 = result2

        else:
            message2, sum2 = get_moto_customs_by_engine_capacity(data["engine_capacity"], True if data["electro_or_no"] == text.lfdp_yes else False, data["auction_price"])

            result1 = await task1

            message1, sum1 = result1

        await state.finish()

        await BothCalculatorByLink.final_stage.set()

        if message1 and message2:
            await bot.send_message(message.chat.id,
                                   message1 + "\n" + message2 + "\n" + "\n" + f"⭐️ ИТОГО: {funcs.sum_prices([sum1, sum2])} по курсу НБРБ на {funcs.get_today_formatted_date()}",
                                   reply_markup=kb_and_vars.final_stage_keybord)

            await bot.send_message(message.chat.id, "Желаете оставить данные для заказа?",
                                   reply_markup=kb_and_vars.final_stage_keybord)
            await bot.send_message(admin_id, "парсер Растаможка+Доставка выполнен")
        else:
            await state.finish()
            await bot.send_message(message.chat.id, "Произошла ошибка, повторите попытку позже",
                                   reply_markup=kb_and_vars.main_menu)


@dp.message_handler(state=BothCalculatorByLink.final_stage)
async def answer_port_of_final_stage(message: types.Message, state: FSMContext):
    answer = message.text
    await state.finish()

    if answer == text.exit_text:
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return
    elif answer == text.send_contact_info_text:
        await ContactInfo.tel_number.set()
        await message.answer("Нажмите кнопку, чтобы поделиться своим контактом для обратной связи:",
                             reply_markup=kb_and_vars.share_contact_keybord)


@dp.message_handler(state=BothCalculatorByLink.go_to_manager_or_no_another_load_type)
async def answer_go_to_manager_or_no_another_load_type(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif answer == text.go_to_manager_text:
        await state.finish()
        await ContactInfo.tel_number.set()
        await message.answer("Нажмите кнопку, чтобы поделиться своим контактом для обратной связи:",
                             reply_markup=kb_and_vars.share_contact_keybord)
    else:
        await BothCalculatorByLink.go_to_manager_or_no_another_load_type.set()
        await message.answer("Выбрана неверная опция, попробуйте еще раз:", reply_markup=kb_and_vars.go_to_manager_menue)
        return