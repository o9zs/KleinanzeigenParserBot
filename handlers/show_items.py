import re
import aiohttp
from bs4 import BeautifulSoup

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

async def get_items(url):
	items = []

	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			body = await response.text()
			soup = BeautifulSoup(body, "html.parser")

			ul = soup.select_one("#srchrslt-content").select_one("div:nth-child(3)").div.ul

			for li in ul.findChildren("li" , recursive=False):
				try:
					main = li.article.select_one(".aditem-main")
					top = main.select_one(".aditem-main--top")
					middle = main.select_one(".aditem-main--middle")

					items.append({
						"location": top.select_one(".aditem-main--top--left").text.strip(),
						"date": top.select_one(".aditem-main--top--right").text.strip(),
						"name": middle.h2.text.strip(),
						"description": middle.p.text.strip(),
						"price": middle.div.text.strip()
					})

				except AttributeError:
					print("AttrError")

	return items

@router.callback_query(F.data.startswith("show_items"))
async def show_items(callback: CallbackQuery):
	href = callback.data.split("=")[1]

	url = "https://www.kleinanzeigen.de" + href

	page = re.search(r"seite:(\d+)", url)
	if page: page = page.group(1)

	output = ""

	for item in await get_items(url):
		item = f"Название: <b>{item['name']}</b>\nОписание: <b>{item['description']}</b>\nЦена: <b>{item['price']}</b>\nДата: <b>{item['date']}</b>\nЛокация: <b>{item['location']}</b>\n\n"

		if len(output) + len(item) >= 4096:
			break

		output += item

	builder = InlineKeyboardBuilder()

	if page:
		previous_page_href = re.sub(r"seite:\d+", f"seite:{int(page) - 1}", href)
		next_page_href = re.sub(r"seite:\d+", f"seite:{int(page) + 1}", href)
	else:
		next_page_href = href + "/seite:2"

	if page and int(page) > 1:
		builder.button(
			text="◀",
			callback_data=f"show_items={previous_page_href}"
		)

	builder.button(
		text=page or "1",
		callback_data="page=" + (page or "1")
	)

	builder.button(
		text="▶",
		callback_data=f"show_items={next_page_href}"
	)

	if page:
		await callback.message.edit_text(
			output,
			parse_mode=ParseMode.HTML,
			reply_markup=builder.as_markup()
		)
	else:
		await callback.message.answer(
			output,
			parse_mode=ParseMode.HTML,
			reply_markup=builder.as_markup()
		)

	await callback.answer()