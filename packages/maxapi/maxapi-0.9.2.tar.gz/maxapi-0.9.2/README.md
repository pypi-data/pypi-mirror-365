# Асинхронный MAX API

[![PyPI version](https://img.shields.io/pypi/v/maxapi.svg)](https://pypi.org/project/maxapi/)
[![Python Version](https://img.shields.io/pypi/pyversions/maxapi.svg)](https://pypi.org/project/maxapi/)
[![License](https://img.shields.io/github/license/love-apples/maxapi.svg)](https://love-apples/maxapi/blob/main/LICENSE)

---

## 📦 Установка

```bash
pip install maxapi
```

---

## 🚀 Быстрый старт

Если вы тестируете бота в чате - не забудьте дать ему права администратора!

```python
import asyncio
import logging

from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, Command, MessageCreated

logging.basicConfig(level=logging.INFO)

bot = Bot('тут_ваш_токен')
dp = Dispatcher()


@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='Привет! Отправь мне /start'
    )


@dp.message_created(Command('start'))
async def hello(event: MessageCreated):
    await event.message.answer(f"Пример чат-бота для MAX 💙")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
```

---

## 📚 Документация

[Тут](https://github.com/love-apples/maxapi/wiki)

---

## ⭐️ Примеры

[Тут](https://github.com/love-apples/maxapi/tree/main/examples)

---


## 🧩 Возможности

- ✅ Middleware
- ✅ Роутеры
- ✅ Билдер инлайн клавиатур
- ✅ Простая загрузка медиафайлов
- ✅ MagicFilter
- ✅ Внутренние функции моделей
- ✅ Контекстный менеджер
- ✅ Поллинг
- ✅ Вебхук
- ✅ Логгирование

---


## 💬 Обратная связь и поддержка

- MAX: [Чат](https://max.ru/join/IPAok63C3vFqbWTFdutMUtjmrAkGqO56YeAN7iyDfc8)
- Telegram: [@loveappless](https://t.me/loveappless)
- Telegram чат: [MAXApi | Обсуждение](https://t.me/maxapi_github)
---

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](https://github.com/love-apples/maxapi/blob/main/LICENSE) для подробностей.
