from aiogram import types
from utils import kb_and_vars, text
from aiogram.dispatcher import FSMContext
from parser_scripts.parser import parse_price
from parser_scripts.select_options_parser import parse_ports_departure_and_delivery
import asyncio
from handlers.bot_manager import dp, bot
from state_models.models import DeliveryPriceCalculator, ContactInfo
from utils import funcs
from config import admin_id
from parser_scripts import actual_locations_keybord_parser
from aiogram.types import ReplyKeyboardRemove

@dp.message_handler(state=DeliveryPriceCalculator.load_type)
async def answer_load_type(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return
    elif answer == text.another or answer == text.load_types_dict[text.pickup]:
        await state.finish()
        await DeliveryPriceCalculator.go_to_manager.set()
        await message.answer("Уточните информацию у менеджера", reply_markup=kb_and_vars.go_to_manager_menue)
        await DeliveryPriceCalculator.go_to_manager_another_load_type.set()

        return

    elif answer not in text.load_types_dict.values():
        await message.answer("Выбран неверный тип транспортного средства, попробуйте еще раз", reply_markup=kb_and_vars.load_type_menue)
        await DeliveryPriceCalculator.load_type.set()
        return

    async with state.proxy() as data:
        data["answer_load_type"] = answer

    await DeliveryPriceCalculator.auction.set()
    await message.answer("📑 Ваш ответ принят, выберете аукцион:", reply_markup=kb_and_vars.auction_type_menue)


@dp.message_handler(state=DeliveryPriceCalculator.go_to_manager_another_load_type)
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
        await message.answer("Выбрана неверная опция, попробуйте еще раз:", reply_markup=kb_and_vars.go_to_manager_menue)
        await DeliveryPriceCalculator.go_to_manager_another_load_type.set()
        return


@dp.message_handler(state=DeliveryPriceCalculator.auction)
async def answer_auction(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif answer not in kb_and_vars.auction_locations_dict.keys():
        await message.answer("Выбран неверный аукцион, попробуйте еще раз", reply_markup=kb_and_vars.auction_type_menue)
        await DeliveryPriceCalculator.auction.set()
        return

    async with state.proxy() as data:
        data["answer_auction"] = answer

        await message.answer("⏳ Идет подбор актуальных площадок отправки...", reply_markup=kb_and_vars.main_menu)

        locations = actual_locations_keybord_parser.parse_actual_locations_keybord(data["answer_auction"],
                                                                               funcs.get_key(text.load_types_dict,
                                                                                             data["answer_load_type"]),
                                                                               message.chat.id)
        locations.pop(0)
        data["actual_locations"] = locations

    await message.answer("📨 Ваш ответ принят, выберете площадку отправки:",
                         reply_markup=kb_and_vars.get_keybord(locations))
    await DeliveryPriceCalculator.location.set()


@dp.message_handler(state=DeliveryPriceCalculator.location)
async def answer_location(message: types.Message, state: FSMContext):
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
            await DeliveryPriceCalculator.location.set()
            return

    async with state.proxy() as data:
        data["answer_location"] = answer

    await DeliveryPriceCalculator.port_of_departure.set()

    await message.answer(text.wait_a_bit)

    async with state.proxy() as data:
        data["ports"], data["ports_delivery"] = parse_ports_departure_and_delivery(data["answer_auction"],
                                                                                   data["answer_location"],
                                                                                   funcs.get_key(text.load_types_dict,
                                                                                        data["answer_load_type"]),
                                                                                        message.chat.id,
                                                                                   data["actual_locations"])
        await message.answer("🚢 Выберете порт отправки:", reply_markup=kb_and_vars.get_keybord(data["ports"]))


@dp.message_handler(state=DeliveryPriceCalculator.port_of_departure)
async def answer_port_of_departure(message: types.Message, state: FSMContext):
    answer = message.text

    async with state.proxy() as data:
        if answer == text.exit_text:
            await state.finish()
            await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
            return
        elif answer not in data["ports"]:
            await message.answer("Выбран неверный порт отправки, попробуйте еще раз",
                                 reply_markup=kb_and_vars.get_keybord(data["ports"]))
            await DeliveryPriceCalculator.port_of_departure.set()
            return

    async with state.proxy() as data:
        data["answer_port_of_departure"] = answer
        await message.answer("🚢 Выберете порт прибытия:", reply_markup=kb_and_vars.get_keybord(data["ports_delivery"]))

    await DeliveryPriceCalculator.port_of_delivery.set()


@dp.message_handler(state=DeliveryPriceCalculator.port_of_delivery)
async def answer_port_of_delivery(message: types.Message, state: FSMContext):
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
                await DeliveryPriceCalculator.port_of_delivery.set()
                return
            else:
                pass

    async with state.proxy() as data:
        data["answer_port_of_delivery"] = answer

    await message.answer("💰 Введите цену транспортного средства в долларах США (например: 10000)",
                         reply_markup=kb_and_vars.exit_kb)

    await DeliveryPriceCalculator.auction_price.set()


@dp.message_handler(state=DeliveryPriceCalculator.auction_price)
async def answer_auction_price(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    elif not answer.isdigit():
        await message.answer("Введите число, а не строку", reply_markup=kb_and_vars.exit_kb)
        await DeliveryPriceCalculator.auction_price.set()
        return

    async with state.proxy() as data:
        data["auction_price"] = answer

    await message.answer("⏳ Ваша цена рассчитывается, ожидайте.", reply_markup=ReplyKeyboardRemove())

    async with state.proxy() as data:
        asyncio.create_task(process_price_parsing(
            message.chat.id,
            funcs.get_key(text.load_types_dict, data["answer_load_type"]),
            data["answer_auction"],
            data["answer_location"],
            data["answer_port_of_departure"],
            data["answer_port_of_delivery"],
            data["ports"],
            data["auction_price"],
            data["actual_locations"],
            is_both_parsers=False,
            state=state)
        )

        await state.finish()


async def process_price_parsing(chat_id: int, load_type, auction, dispatch_site, port_of_departure, port_of_delivery,
                                ports, auction_price, actual_locations, is_both_parsers, state):
    try:

        final_message, total = parse_price(load_type, auction, dispatch_site, port_of_departure, port_of_delivery, ports,
                                          auction_price, chat_id, actual_locations)


        if not is_both_parsers:
            if final_message:
                await bot.send_message(chat_id, final_message, reply_markup=kb_and_vars.main_menu)
                await bot.send_message(admin_id, "парсер Доставка выполнен")
                await DeliveryPriceCalculator.final_stage.set()
                await bot.send_message(chat_id, "Желаете оставить данные для заказа?",
                                       reply_markup=kb_and_vars.final_stage_keybord)
            else:
                await state.finish()
                await bot.send_message(chat_id, "Произошла ошибка, повторите попытку позже",
                                       reply_markup=kb_and_vars.main_menu)
        else:
            return final_message, total

    except Exception as _:
        await bot.send_message(chat_id, "Произошла ошибка, повторите попытку позже", reply_markup=kb_and_vars.main_menu)


@dp.message_handler(state=DeliveryPriceCalculator.final_stage)
async def answer_final_stage(message: types.Message, state: FSMContext):
    answer = message.text
    await state.finish()

    if answer == text.exit_text:
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return
    elif answer == text.send_contact_info_text:
        await ContactInfo.tel_number.set()
        await message.answer("Нажмите кнопку, чтобы поделиться своим контактом для обратной связи:",
                             reply_markup=kb_and_vars.share_contact_keybord)


@dp.message_handler(state=DeliveryPriceCalculator.go_to_manager)
async def go_to_manager(message: types.Message, state: FSMContext):
    answer = message.text

    if answer == text.go_to_manager_text:
        await state.finish()
        await ContactInfo.tel_number.set()
        await message.answer("Нажмите кнопку, чтобы поделиться своим контактом для обратной связи:",
                             reply_markup=kb_and_vars.share_contact_keybord)