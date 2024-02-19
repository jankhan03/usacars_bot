from aiogram import types
from utils import kb_and_vars, text
from aiogram.dispatcher import FSMContext
from handlers.bot_manager import dp
from state_models.models import CarCustomsCalculator, ContactInfo
import asyncio
from parser_scripts.car_customs_calculator_parser import parse_car_customs_price
from handlers.bot_manager import bot
from datetime import datetime
from utils.funcs import get_moto_customs_by_engine_capacity
from config import admin_id
from aiogram.types import ReplyKeyboardRemove


@dp.message_handler(state=CarCustomsCalculator.car_age)
async def answer_car_age(message: types.Message, state: FSMContext):
    answer = message.text
    today_year = int(datetime.today().year)

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif not answer.isdigit():
        await CarCustomsCalculator.car_age.set()
        await message.answer("Введите число, а не строку:", reply_markup=kb_and_vars.exit_kb)
        return
    elif int(answer) < 0:
        await CarCustomsCalculator.car_age.set()
        await message.answer("Год должен быть >0 :", reply_markup=kb_and_vars.exit_kb)
        return
    elif today_year < int(answer):
        await CarCustomsCalculator.car_age.set()
        await message.answer(f"Число не может быть больше, чем {today_year} :", reply_markup=kb_and_vars.exit_kb)
        return

    async with state.proxy() as data:

        data["car_age"] = today_year - int(answer)

    await CarCustomsCalculator.electro_or_no.set()

    await message.answer("⚡️Электрический транспорт?",
                         reply_markup=kb_and_vars.lfdp_choice_menue)


@dp.message_handler(state=CarCustomsCalculator.electro_or_no)
async def answer_car_age_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif answer not in [text.lfdp_yes, text.lfdp_no]:
        await CarCustomsCalculator.electro_or_no.set()
        await message.answer("Выбран неверный вариант, попробуйте еще раз:", reply_markup=kb_and_vars.lfdp_choice_menue)
        return

    async with state.proxy() as data:
        data["electro_or_no"] = answer

    await CarCustomsCalculator.motorcycle.set()
    await message.answer("🏍️ Мотоцикл?",
                         reply_markup=kb_and_vars.lfdp_choice_menue)


@dp.message_handler(state=CarCustomsCalculator.motorcycle)
async def answer_car_age_two(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif answer not in [text.lfdp_yes, text.lfdp_no]:
        await CarCustomsCalculator.motorcycle.set()
        await message.answer("Выбран неверный вариант, попробуйте еще раз:", reply_markup=kb_and_vars.lfdp_choice_menue)
        return

    async with state.proxy() as data:
        data["motorcycle"] = answer

    await CarCustomsCalculator.car_price.set()
    await message.answer("💰 Введите цену транспортного средства в долларах США (например: 10000)",
                         reply_markup=kb_and_vars.exit_kb)


@dp.message_handler(state=CarCustomsCalculator.car_price)
async def answer_car_price(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif not answer.isdigit():
        await CarCustomsCalculator.car_price.set()
        await message.answer("Введите число, а не строку:", reply_markup=kb_and_vars.exit_kb)
        return

    async with state.proxy() as data:
        data["car_price"] = answer
        if data["electro_or_no"] == text.lfdp_no:
            await CarCustomsCalculator.engine_capacity.set()
            if data["motorcycle"] == text.lfdp_yes:
                await message.answer("⛽️ Введите объем двигателя (например 650 см3)", reply_markup=kb_and_vars.exit_kb)
            else:
                await message.answer("⛽️ Введите объем двигателя в см. куб. (2 литра = 2000 см. куб.)",
                                     reply_markup=kb_and_vars.exit_kb)
        else:
            data["engine_capacity"] = "2000"
            await CarCustomsCalculator.lfdp_choice.set()
            await message.answer("📄 Льготная таможня под 1️⃣4️⃣0️⃣ указ?", reply_markup=kb_and_vars.lfdp_choice_menue)


@dp.message_handler(state=CarCustomsCalculator.engine_capacity)
async def answer_engine_capacity(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif not answer.isdigit():
        await CarCustomsCalculator.engine_capacity.set()
        await message.answer("Введите число, а не строку:", reply_markup=kb_and_vars.exit_kb)
        return
    elif int(answer) <= 0:
        await CarCustomsCalculator.engine_capacity.set()
        await message.answer("Введите число, отличное от нуля", reply_markup=kb_and_vars.exit_kb)
        return

    async with state.proxy() as data:
        data["engine_capacity"] = answer
        if data["motorcycle"] == text.lfdp_yes:
            await message.answer("⏳ Ваша таможенная цена рассчитывается, подождите", reply_markup=kb_and_vars.main_menu)
            msg, total = get_moto_customs_by_engine_capacity(data["engine_capacity"], True if data["electro_or_no"] == text.lfdp_yes else False, data["car_price"])
            await message.answer(msg, reply_markup=kb_and_vars.main_menu)

            await CarCustomsCalculator.final_stage.set()
            await bot.send_message(message.chat.id, "Желаете оставить данные для заказа?",
                                   reply_markup=kb_and_vars.final_stage_keybord)

            return

    await CarCustomsCalculator.lfdp_choice.set()
    await message.answer("📄 Льготная таможня под 1️⃣4️⃣0️⃣ указ?", reply_markup=kb_and_vars.lfdp_choice_menue)


@dp.message_handler(state=CarCustomsCalculator.lfdp_choice)
async def answer_lfdp_choice(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif answer not in [text.lfdp_yes, text.lfdp_no]:
        await CarCustomsCalculator.lfdp_choice.set()
        await message.answer("Выбран неверный вариант, попробуйте еще раз:", reply_markup=kb_and_vars.lfdp_choice_menue)
        return

    async with state.proxy() as data:
        data["lfdp_choice"] = answer

    await message.answer("⏳ Ваша таможенная цена рассчитывается, подождите", reply_markup=ReplyKeyboardRemove())

    async with state.proxy() as data:
        asyncio.create_task(precalculating_car_customs(
                                                    data["car_age"],
                                                    data["car_price"],
                                                    data["engine_capacity"],
                                                    data["lfdp_choice"],
                                                    message.chat.id,
                                                    data["electro_or_no"],
                                                    is_both_parsers=False, state=state)
                            )

        await state.finish()


async def precalculating_car_customs(car_age, car_price, engine_capacity, lfdp, chat_id, electro_or_no,
            is_both_parsers, state):
    try:
        final_message, sum_dollars = parse_car_customs_price(car_age, car_price, engine_capacity, lfdp, electro_or_no, chat_id)

        if not is_both_parsers:
            if final_message:
                await bot.send_message(chat_id, final_message, reply_markup=kb_and_vars.main_menu)
                await bot.send_message(admin_id, "парсер Растаможка выполнен")
                await CarCustomsCalculator.final_stage.set()
                await bot.send_message(chat_id, "Желаете оставить данные для заказа?",
                                       reply_markup=kb_and_vars.final_stage_keybord)
            else:
                await state.finish()
                await bot.send_message(chat_id, "Произошла ошибка, повторите попытку позже",
                                       reply_markup=kb_and_vars.main_menu)
        else:
            return final_message, sum_dollars

    except Exception as _:
        await bot.send_message(chat_id, "Произошла ошибка, повторите попытку позже", reply_markup=kb_and_vars.main_menu)


@dp.message_handler(state=CarCustomsCalculator.go_to_manager)
async def go_to_manager(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.go_to_manager_text:
        await state.finish()
        await ContactInfo.tel_number.set()
        await message.answer("Нажмите кнопку, чтобы поделиться своим контактом для обратной связи:",
                             reply_markup=kb_and_vars.share_contact_keybord)


@dp.message_handler(state=CarCustomsCalculator.final_stage)
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
