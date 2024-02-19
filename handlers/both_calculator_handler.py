from aiogram import types
from utils import kb_and_vars, text
from aiogram.dispatcher import FSMContext
from handlers.bot_manager import dp, bot
from state_models.models import BothCalculator, ContactInfo
from parser_scripts.select_options_parser import parse_ports_departure_and_delivery
import asyncio
from handlers.car_customs_calculator_handler import precalculating_car_customs
from utils import funcs
from datetime import datetime
from utils.funcs import get_moto_customs_by_engine_capacity
from handlers.price_calculator_handler import process_price_parsing
from config import admin_id
from parser_scripts import actual_locations_keybord_parser
from aiogram.types import ReplyKeyboardRemove


@dp.message_handler(state=BothCalculator.load_type)
async def answer_load_type_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return
    elif answer == text.another or answer == text.load_types_dict[text.pickup]:
        await state.finish()
        await BothCalculator.go_to_manager.set()
        await message.answer("Уточните информацию у менеджера", reply_markup=kb_and_vars.go_to_manager_menue)
        await BothCalculator.go_to_manager_or_no_another_load_type.set()
        return

    elif answer not in text.load_types_dict.values():
        await message.answer("Выбран неверный load type, попробуйте еще раз", reply_markup=kb_and_vars.load_type_menue)
        await BothCalculator.load_type.set()
        return

    async with state.proxy() as data:
        data["answer_load_type"] = answer
        data["motorcycle"] = text.lfdp_yes if funcs.get_key(text.load_types_dict, data["answer_load_type"]) == text.motorcycle else text.lfdp_no

    await message.answer("Введите год выпуска вашего транспортного средства (например 2018):", reply_markup=kb_and_vars.exit_kb)

    await BothCalculator.car_age.set()


@dp.message_handler(state=BothCalculator.go_to_manager_or_no_another_load_type)
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
        await BothCalculator.go_to_manager_or_no_another_load_type.set()
        await message.answer("Выбрана неверная опция, попробуйте еще раз:", reply_markup=kb_and_vars.go_to_manager_menue)
        return


@dp.message_handler(state=BothCalculator.car_age)
async def answer_car_age(message: types.Message, state: FSMContext):
    answer = message.text
    today_year = int(datetime.today().year)

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif not answer.isdigit():
        await BothCalculator.car_age.set()
        await message.answer("Введите число, а не строку:", reply_markup=kb_and_vars.exit_kb)
        return
    elif int(answer) < 0:
        await BothCalculator.car_age.set()
        await message.answer("Год должен быть >0 :", reply_markup=kb_and_vars.exit_kb)
        return
    elif today_year < int(answer):
        await BothCalculator.car_age.set()
        await message.answer(f"Число не может быть больше, чем {today_year} :", reply_markup=kb_and_vars.exit_kb)
        return

    async with state.proxy() as data:

        data["car_age"] = today_year - int(answer)

    await BothCalculator.electro_or_no.set()

    await message.answer("⚡️Электрический транспорт?",
                         reply_markup=kb_and_vars.lfdp_choice_menue)


@dp.message_handler(state=BothCalculator.electro_or_no)
async def answer_car_age_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif answer not in [text.lfdp_yes, text.lfdp_no]:
        await BothCalculator.electro_or_no.set()
        await message.answer("Выбран неверный вариант, попробуйте еще раз:", reply_markup=kb_and_vars.lfdp_choice_menue)
        return

    async with state.proxy() as data:
        data["electro_or_no"] = answer
        if data["electro_or_no"] == text.lfdp_no:
            await BothCalculator.engine_capacity.set()

            if data["motorcycle"] == text.lfdp_yes:
                await message.answer("⛽️ Введите объем двигателя (например 650 см3)", reply_markup=kb_and_vars.exit_kb)
            else:
                await message.answer("⛽️ Введите объем двигателя в см. куб. (2 литра = 2000 см. куб.)",
                                     reply_markup=kb_and_vars.exit_kb)
        else:
            data["engine_capacity"] = "2000"
            await BothCalculator.lfdp_choice.set()
            await message.answer("📄 Льготная таможня под 1️⃣4️⃣0️⃣ указ?", reply_markup=kb_and_vars.lfdp_choice_menue)

@dp.message_handler(state=BothCalculator.engine_capacity)
async def answer_engine_capacity_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif not answer.isdigit():
        await BothCalculator.engine_capacity.set()
        await message.answer("Введите число, а не строку:", reply_markup=kb_and_vars.exit_kb)
        return

    elif int(answer) <= 0:
        await BothCalculator.engine_capacity.set()
        await message.answer("Введите число больше нуля", reply_markup=kb_and_vars.exit_kb)
        return

    async with state.proxy() as data:
        data["engine_capacity"] = answer

        if data["motorcycle"] == text.lfdp_yes:

            await BothCalculator.auction.set()

            await message.answer("📑 Ваш ответ принят, выберете аукцион:", reply_markup=kb_and_vars.auction_type_menue)
            return

    await BothCalculator.lfdp_choice.set()
    await message.answer("📄 Льготная таможня под 1️⃣4️⃣0️⃣ указ?", reply_markup=kb_and_vars.lfdp_choice_menue)


@dp.message_handler(state=BothCalculator.lfdp_choice)
async def answer_lfdp_choice_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif answer not in [text.lfdp_yes, text.lfdp_no]:
        await BothCalculator.lfdp_choice.set()
        await message.answer("Выбран неверный вариант, попробуйте еще раз:", reply_markup=kb_and_vars.lfdp_choice_menue)
        return

    async with state.proxy() as data:
        data["lfdp_choice"] = answer

    await BothCalculator.auction.set()

    await message.answer("📑 Ваш ответ принят, выберете аукцион:", reply_markup=kb_and_vars.auction_type_menue)


@dp.message_handler(state=BothCalculator.auction)
async def answer_auction_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif answer not in kb_and_vars.auction_locations_dict.keys():
        await message.answer("Выбран неверный аукцион, попробуйте еще раз", reply_markup=kb_and_vars.auction_type_menue)
        await BothCalculator.auction.set()
        return

    async with state.proxy() as data:
        data["answer_auction"] = answer

        await message.answer("⏳ Идет подбор актуальных площадок отправки...", reply_markup=kb_and_vars.main_menu)

        locations = actual_locations_keybord_parser.parse_actual_locations_keybord(data["answer_auction"],
                                                                                   funcs.get_key(text.load_types_dict,
                                                                                                 data[
                                                                                                     "answer_load_type"]),
                                                                                   message.chat.id)
        locations.pop(0)
        data["actual_locations"] = locations

    await message.answer("📨 Ваш ответ принят, выберете площадку отправки:",
                         reply_markup=kb_and_vars.get_keybord(locations))
    await BothCalculator.location.set()


@dp.message_handler(state=BothCalculator.location)
async def answer_location_two(message: types.Message, state: FSMContext):
    answer = message.text

    async with state.proxy() as data:
        if answer == text.exit_text:
            await state.finish()
            await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
            return
        elif answer not in kb_and_vars.auction_locations_dict[data["answer_auction"]]:
            await message.answer("Выбран неверная площадка отправки, попробуйте еще раз",
                                 reply_markup=
                                 kb_and_vars.get_keybord(kb_and_vars.auction_locations_dict[data["answer_auction"]]))
            await BothCalculator.location.set()
            return

    async with state.proxy() as data:
        data["answer_location"] = answer

    await BothCalculator.port_of_departure.set()

    await message.answer(text.wait_a_bit)

    async with state.proxy() as data:
        data["ports"], data["ports_delivery"] = parse_ports_departure_and_delivery(data["answer_auction"],
                                                                                   data["answer_location"],
                                                                                   funcs.get_key(text.load_types_dict,
                                                                                                 data[
                                                                                                     "answer_load_type"]),
                                                                                   message.chat.id,
                                                                                   data["actual_locations"])
        await message.answer("🚢 Выберете порт отправки:", reply_markup=kb_and_vars.get_keybord(data["ports"]))


@dp.message_handler(state=BothCalculator.port_of_departure)
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
            await BothCalculator.port_of_departure.set()
            return

    async with state.proxy() as data:
        data["answer_port_of_departure"] = answer
        await message.answer("🚢 Выберете порт прибытия:", reply_markup=kb_and_vars.get_keybord(data["ports_delivery"]))

    await BothCalculator.port_of_delivery.set()


@dp.message_handler(state=BothCalculator.port_of_delivery)
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
                await BothCalculator.port_of_delivery.set()
                return
            else:
                pass

    async with state.proxy() as data:
        data["answer_port_of_delivery"] = answer

    await message.answer("💰 Введите цену транспортного средства в долларах США (например: 10000)",
                         reply_markup=kb_and_vars.exit_kb)

    await BothCalculator.auction_price.set()


@dp.message_handler(state=BothCalculator.auction_price)
async def answer_auction_price_two(message: types.Message, state: FSMContext):
    answer = message.text

    if not answer.isdigit():
        await message.answer("Введите число, а не строку", reply_markup=kb_and_vars.exit_kb)
        await BothCalculator.auction_price.set()
        return

    async with state.proxy() as data:
        data["auction_price"] = answer

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

        await BothCalculator.final_stage.set()

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


@dp.message_handler(state=BothCalculator.go_to_manager)
async def go_to_manager(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.go_to_manager_text:
        await state.finish()
        await ContactInfo.tel_number.set()
        await message.answer("Нажмите кнопку, чтобы поделиться своим контактом для обратной связи:",
                             reply_markup=kb_and_vars.share_contact_keybord)


@dp.message_handler(state=BothCalculator.final_stage)
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
