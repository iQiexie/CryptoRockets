from aiogram import Dispatcher

from app.telegram.routes import start, payment

root_dispatcher = Dispatcher()
root_dispatcher.include_router(start.router)
root_dispatcher.include_router(payment.router)
