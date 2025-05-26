from aiogram import Dispatcher

from app.telegram.routes import start

root_dispatcher = Dispatcher()
root_dispatcher.include_router(start.router)
