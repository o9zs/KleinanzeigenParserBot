import re
import aiohttp
from bs4 import BeautifulSoup

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

class PriceForm(StatesGroup):
	price_range = State()

@router.message(CommandStart())
async def select_price(message: Message, state: FSMContext):
	await state.set_state(PriceForm.price_range)

	await message.answer("Напишите диапазон цены через дефис, например 1000-1500:")

@router.message(PriceForm.price_range)
async def confirm_price(message: Message, state: FSMContext):
	data = await state.update_data(amount=message.text)
	price_range = data["amount"].split("-")

	if len(price_range) != 2:
		return await message.answer("Некорректный ввод")

	try:
		minimum = float(price_range[0])
		maximum = float(price_range[1])
	except ValueError:
		return await message.answer("Некорректный ввод")
	
	if minimum > maximum:
		return await message.answer("Меньшее больше большего")

	await state.clear()

	url = "https://www.kleinanzeigen.de/s-kategorien.html"

	builder = InlineKeyboardBuilder()

	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			body = await response.text()
			soup = BeautifulSoup(body, "html.parser")

			div = soup.select_one("main").select_one("div:nth-child(2)")

			for ul in div.findChildren("ul" , recursive=False):
				for li in ul.findChildren("li" , recursive=False):
					href =  re.sub(r"/preis:\d*:\d*", '', li.h2.a.get("href"))
					href = href + f"/preis:{minimum:g}:{maximum:g}"

					print(href)

					builder.button(
						text=li.h2.text.split("(")[0].strip(),
						callback_data="show_items=" + href
					)

	builder.adjust(3)

	await message.answer(
		f"Выбранный диапозон: от {minimum:g} до {maximum:g}",
		reply_markup=builder.as_markup()
	)