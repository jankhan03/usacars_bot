from handlers.start_handler import *
from handlers.price_calculator_handler import *
from handlers.contact_info_handler import *
from handlers.car_customs_calculator_handler import *
from handlers.both_calculator_handler import *
from handlers.bot_calculator_by_link_handler import *
from aiogram import executor
from handlers.bot_manager import dp

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
