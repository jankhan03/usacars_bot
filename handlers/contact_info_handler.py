import config
from utils import kb_and_vars, text
from aiogram.dispatcher import FSMContext
from handlers.bot_manager import dp, bot
from state_models.models import ContactInfo
from aiogram import types


@dp.message_handler(state=ContactInfo.tel_number, content_types=[types.ContentType.CONTACT, types.ContentType.TEXT])
async def answer_contact_info(message: types.Message, state: FSMContext):
    if message.text == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return
    else:
        if message.contact:
            contact = message.contact

            phone_number = contact.phone_number
            first_name = contact.first_name
            last_name = contact.last_name

            async with state.proxy() as data:
                data["phone_number"] = phone_number
                data["first_name"] = first_name

            await ContactInfo.message.set()

            await message.answer("Введите сообщение, которое хотите передать:", reply_markup=kb_and_vars.exit_kb)

        else:
            await ContactInfo.tel_number.set()
            await message.answer("Выбрана неверная опция, повторите еще раз",
                                    reply_markup=kb_and_vars.share_contact_keybord)


@dp.message_handler(state=ContactInfo.message)
async def answer_message(message: types.Message, state: FSMContext):
    if message.text == text.exit_text:
        await state.finish()
        await message.answer(text.going_to_menue_text, reply_markup=kb_and_vars.main_menu)
        return

    await message.answer("Спасибо, с вами скоро свяжутся.", reply_markup=kb_and_vars.main_menu)

    try:
        async with state.proxy() as data:
            for id in config.amin_ids_list:
                await bot.send_message(id, f"Контакт:\n---------------------------\n{data['first_name']}"
                                           f"\n{data['phone_number']}\n---------"
                                           f"------------------\nСообщение:\n---------------------------\n{message.text}")
    except Exception as error:
        print(error)
    await state.finish()