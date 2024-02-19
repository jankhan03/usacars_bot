from aiogram import types
from utils import kb_and_vars, text
from handlers.bot_manager import dp
from state_models.models import DeliveryPriceCalculator, ContactInfo, CarCustomsCalculator, BothCalculator,\
    BothCalculatorByLink


@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    await message.answer(text=text.start_message_text, reply_markup=kb_and_vars.main_menu)


@dp.message_handler(commands=["get_id"])
async def get_id(message: types.Message) -> None:
    await message.answer(message.chat.id)


@dp.message_handler()
async def general_message_handler(message: types.Message, state=None) -> None:
    if message.text == text.go_to_calculator_text:
        await DeliveryPriceCalculator.load_type.set()
        await message.answer("🚗 Выберите тип транспортного средства:", reply_markup=kb_and_vars.load_type_menue)
    elif message.text == text.exit_text:
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
    elif message.text == text.send_contact_info_text:
        await ContactInfo.tel_number.set()
        await message.answer("ℹ️ Нажмите кнопку, чтобы поделиться своим контактом для обратной связи:",
                             reply_markup=kb_and_vars.share_contact_keybord)
    elif message.text == text.go_to_car_customs_clearance_calculator_text:
        await CarCustomsCalculator.car_age.set()
        await message.answer("✅ Введите год выпуска вашего транспортного средства (например 2018):", reply_markup=kb_and_vars.exit_kb)
    elif message.text == text.go_to_both_text:
        await BothCalculator.load_type.set()
        await message.answer("🚗 Выберите тип транспортного средства:", reply_markup=kb_and_vars.load_type_menue)
    elif message.text == text.go_to_both_by_link_text:
        await BothCalculatorByLink.load_type.set()
        await message.answer("🚗 Выберите тип транспортного средства:", reply_markup=kb_and_vars.load_type_menue)
