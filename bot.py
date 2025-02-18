import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import TOKEN
from handlers import show_items

logging.basicConfig(level=logging.INFO, format='\x1b[30;1m%(asctime)s\x1b[0m \x1b[34;1m%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

async def main():
	from handlers import start, show_items
	
	bot = Bot(token=TOKEN)

	dispatcher = Dispatcher()
	dispatcher.include_routers(
		start.router,
		show_items.router
	)

	await dispatcher.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
