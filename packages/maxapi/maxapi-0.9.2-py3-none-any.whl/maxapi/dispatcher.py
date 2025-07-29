from __future__ import annotations

import asyncio

from typing import Any, Callable, Dict, List, TYPE_CHECKING, Optional
from asyncio.exceptions import TimeoutError as AsyncioTimeoutError

from aiohttp import ClientConnectorError

from .filters.middleware import BaseMiddleware
from .filters.handler import Handler

from .context import MemoryContext
from .types.updates import UpdateUnion
from .types.errors import Error

from .methods.types.getted_updates import process_update_request, process_update_webhook

from .filters import filter_attrs

from .bot import Bot
from .enums.update import UpdateType
from .loggers import logger_dp


try:
    from fastapi import FastAPI, Request # type: ignore
    from fastapi.responses import JSONResponse # type: ignore
    FASTAPI_INSTALLED = True
except ImportError:
    FASTAPI_INSTALLED = False
    
    
try:
    from uvicorn import Config, Server # type: ignore
    UVICORN_INSTALLED = True
except ImportError:
    UVICORN_INSTALLED = False
    

if TYPE_CHECKING:
    from magic_filter import MagicFilter

CONNECTION_RETRY_DELAY = 30
GET_UPDATES_RETRY_DELAY = 5


class Dispatcher:
    
    """
    Основной класс для обработки событий бота.

    Обеспечивает запуск поллинга и вебхука, маршрутизацию событий,
    применение middleware, фильтров и вызов соответствующих обработчиков.
    """
    
    def __init__(self, router_id: str | None = None) -> None:
        
        """
        Инициализация диспетчера.
        """
        
        self.router_id = router_id
        
        self.event_handlers: List[Handler] = []
        self.contexts: List[MemoryContext] = []
        self.routers: List[Router | Dispatcher] = []
        self.filters: List[MagicFilter] = []
        self.middlewares: List[BaseMiddleware] = []
        
        self.bot: Optional[Bot] = None
        self.webhook_app: Optional[FastAPI] = None
        self.on_started_func: Optional[Callable] = None

        self.message_created = Event(update_type=UpdateType.MESSAGE_CREATED, router=self)
        self.bot_added = Event(update_type=UpdateType.BOT_ADDED, router=self)
        self.bot_removed = Event(update_type=UpdateType.BOT_REMOVED, router=self)
        self.bot_started = Event(update_type=UpdateType.BOT_STARTED, router=self)
        self.bot_stopped = Event(update_type=UpdateType.BOT_STOPPED, router=self)
        self.dialog_cleared = Event(update_type=UpdateType.DIALOG_CLEARED, router=self)
        self.dialog_muted = Event(update_type=UpdateType.DIALOG_MUTED, router=self)
        self.dialog_unmuted = Event(update_type=UpdateType.DIALOG_UNMUTED, router=self)
        self.chat_title_changed = Event(update_type=UpdateType.CHAT_TITLE_CHANGED, router=self)
        self.message_callback = Event(update_type=UpdateType.MESSAGE_CALLBACK, router=self)
        self.message_chat_created = Event(update_type=UpdateType.MESSAGE_CHAT_CREATED, router=self)
        self.message_edited = Event(update_type=UpdateType.MESSAGE_EDITED, router=self)
        self.message_removed = Event(update_type=UpdateType.MESSAGE_REMOVED, router=self)
        self.user_added = Event(update_type=UpdateType.USER_ADDED, router=self)
        self.user_removed = Event(update_type=UpdateType.USER_REMOVED, router=self)
        self.on_started = Event(update_type=UpdateType.ON_STARTED, router=self)
        
    def webhook_post(self, path: str):
        def decorator(func):
            if self.webhook_app is None:
                try:
                    from fastapi import FastAPI # type: ignore
                except ImportError:
                    raise ImportError(
                        '\n\t Не установлен fastapi!'
                        '\n\t Выполните команду для установки fastapi: '
                        '\n\t pip install fastapi>=0.68.0'
                        '\n\t Или сразу все зависимости для работы вебхука:'
                        '\n\t pip install maxapi[webhook]'
                    )
                self.webhook_app = FastAPI()
            return self.webhook_app.post(path)(func)
        return decorator
        
    async def check_me(self):
        
        """
        Проверяет и логирует информацию о боте.
        """
        
        me = await self.bot.get_me()
        
        self.bot._me = me
        
        logger_dp.info(f'Бот: @{me.username} first_name={me.first_name} id={me.user_id}')

    def include_routers(self, *routers: 'Router'):
        
        """
        Добавляет указанные роутеры в диспетчер.

        :param routers: Роутеры для добавления.
        """
        
        self.routers += [r for r in routers]
            
    async def __ready(self, bot: Bot):
        
        """
        Подготавливает диспетчер: сохраняет бота, регистрирует обработчики, вызывает on_started.

        :param bot: Экземпляр бота.
        """
        
        self.bot = bot
        
        await self.check_me()
        
        self.routers += [self]
        
        handlers_count = sum(len(router.event_handlers) for router in self.routers)

        logger_dp.info(f'{handlers_count} событий на обработку')

        if self.on_started_func:
            await self.on_started_func()
            
    def __get_memory_context(self, chat_id: int, user_id: int):
        
        """
        Возвращает существующий или создает новый контекст по chat_id и user_id.

        :param chat_id: Идентификатор чата.
        :param user_id: Идентификатор пользователя.
        :return: Объект MemoryContext.
        """

        for ctx in self.contexts:
            if ctx.chat_id == chat_id and ctx.user_id == user_id:
                return ctx
            
        new_ctx = MemoryContext(chat_id, user_id)
        self.contexts.append(new_ctx)
        return new_ctx
        
    async def process_middlewares(
            self,
            middlewares: List[BaseMiddleware],
            event_object: UpdateUnion,
            result_data_kwargs: Dict[str, Any]
        ):
        
        """
        Последовательно обрабатывает middleware цепочку.

        :param middlewares: Список middleware.
        :param event_object: Объект события.
        :param result_data_kwargs: Аргументы, передаваемые обработчику.
        :return: Изменённые аргументы или None.
        """
        
        for middleware in middlewares:
            result = await middleware.process_middleware(
                event_object=event_object,
                result_data_kwargs=result_data_kwargs
            )
            
            if result is None or result is False:
                return
            
            elif result is True:
                continue
            
            result_data_kwargs.update(result)
        
        return result_data_kwargs

    async def handle(self, event_object: UpdateUnion):
        
        """
        Основной обработчик события. Применяет фильтры, middleware и вызывает подходящий handler.

        :param event_object: Событие, пришедшее в бот.
        """
        
        try:
            ids = event_object.get_ids()
            memory_context = self.__get_memory_context(*ids)
            current_state = await memory_context.get_state()
            kwargs = {'context': memory_context}
            router_id = None
            
            process_info = f'{event_object.update_type} | chat_id: {ids[0]}, user_id: {ids[1]}'
            
            is_handled = False
            
            for index, router in enumerate(self.routers):
                
                if is_handled:
                    break
                
                router_id = router.router_id or index
                
                if router.filters:
                    if not filter_attrs(event_object, *router.filters):
                        continue
                    
                kwargs = await self.process_middlewares(
                    middlewares=router.middlewares,
                    event_object=event_object,
                    result_data_kwargs=kwargs
                )
                
                for handler in router.event_handlers:

                    if not handler.update_type == event_object.update_type:
                        continue

                    if handler.filters:
                        if not filter_attrs(event_object, *handler.filters):
                            continue

                    if not handler.state == current_state and handler.state:
                        continue
                    
                    func_args = handler.func_event.__annotations__.keys()
                    
                    kwargs = await self.process_middlewares(
                        middlewares=handler.middlewares,
                        event_object=event_object,
                        result_data_kwargs=kwargs
                    )
                    
                    if not kwargs:
                        continue
                        
                    for key in kwargs.copy().keys():
                        if key not in func_args:
                            del kwargs[key]
                        
                    await handler.func_event(event_object, **kwargs)

                    logger_dp.info(f'Обработано: {router_id} | {process_info}')

                    is_handled = True
                    break

            if not is_handled:
                logger_dp.info(f'Проигнорировано: {router_id} | {process_info}')
            
        except Exception as e:
            logger_dp.error(f"Ошибка при обработке события: {router_id} | {process_info} | {e} ")

    async def start_polling(self, bot: Bot):
        
        """
        Запускает цикл получения обновлений с сервера (long polling).

        :param bot: Экземпляр бота.
        """
        
        await self.__ready(bot)

        while True:
            
            if self.bot is None:
                raise RuntimeError('Bot не инициализирован')
                
            try:
                events: Dict = await self.bot.get_updates()
            except AsyncioTimeoutError:
                continue
        
            try:

                if isinstance(events, Error):
                    logger_dp.info(f'Ошибка при получении обновлений: {events}, жду {GET_UPDATES_RETRY_DELAY} секунд')
                    await asyncio.sleep(GET_UPDATES_RETRY_DELAY)
                    continue

                self.bot.marker_updates = events.get('marker')
 
                processed_events = await process_update_request(
                    events=events,
                    bot=self.bot
                )
                
                for event in processed_events:
                    await self.handle(event)
                    
            except ClientConnectorError:
                logger_dp.error(f'Ошибка подключения, жду {CONNECTION_RETRY_DELAY} секунд')
                await asyncio.sleep(CONNECTION_RETRY_DELAY)
            except Exception as e:
                logger_dp.error(f'Общая ошибка при обработке событий: {e.__class__} - {e}')

    async def handle_webhook(self, bot: Bot, host: str = 'localhost', port: int = 8080, **kwargs):
        
        """
        Запускает FastAPI-приложение для приёма обновлений через вебхук.

        :param bot: Экземпляр бота.
        :param host: Хост, на котором запускается сервер.
        :param port: Порт сервера.
        """
        
        if not FASTAPI_INSTALLED:
            raise ImportError(
                '\n\t Не установлен fastapi!'
                '\n\t Выполните команду для установки fastapi: '
                '\n\t pip install fastapi>=0.68.0'
                '\n\t Или сразу все зависимости для работы вебхука:'
                '\n\t pip install maxapi[webhook]'
            )
            
        elif not UVICORN_INSTALLED:
            raise ImportError(
                '\n\t Не установлен uvicorn!'
                '\n\t Выполните команду для установки uvicorn: '
                '\n\t pip install uvicorn>=0.15.0'
                '\n\t Или сразу все зависимости для работы вебхука:'
                '\n\t pip install maxapi[webhook]'
            )
        
        # try:
        #     from fastapi import Request
        #     from fastapi.responses import JSONResponse
        # except ImportError:
        #     raise ImportError(
        #         '\n\t Не установлен fastapi!'
        #         '\n\t Выполните команду для установки fastapi: '
        #         '\n\t pip install fastapi>=0.68.0'
        #         '\n\t Или сразу все зависимости для работы вебхука:'
        #         '\n\t pip install maxapi[webhook]'
        #     )
            
        
        @self.webhook_post('/')
        async def _(request: Request):
            event_json = await request.json()
            event_object = await process_update_webhook(
                event_json=event_json,
                bot=bot
            )
            
            await self.handle(event_object)
            return JSONResponse(content={'ok': True}, status_code=200)
        
        
        await self.init_serve(
            bot=bot,
            host=host,
            port=port, 
            **kwargs
        )
        
    async def init_serve(self, bot: Bot, host: str = 'localhost', port: int = 8080, **kwargs):
    
        """
        Запускает сервер для обработки входящих вебхуков.

        :param bot: Экземпляр бота.
        :param host: Хост, на котором запускается сервер.
        :param port: Порт сервера.
        """
        
        # try:
        #     from uvicorn import Config, Server
        # except ImportError:
        #     raise ImportError(
        #         '\n\t Не установлен uvicorn!'
        #         '\n\t Выполните команду для установки uvicorn: '
        #         '\n\t pip install uvicorn>=0.15.0'
        #         '\n\t Или сразу все зависимости для работы вебхука:'
        #         '\n\t pip install maxapi[webhook]'
        #     )
        
        if not UVICORN_INSTALLED:
            raise ImportError(
                '\n\t Не установлен uvicorn!'
                '\n\t Выполните команду для установки uvicorn: '
                '\n\t pip install uvicorn>=0.15.0'
                '\n\t Или сразу все зависимости для работы вебхука:'
                '\n\t pip install maxapi[webhook]'
            )
            
        if self.webhook_app is None:
            raise RuntimeError('webhook_app не инициализирован')
            
        config = Config(app=self.webhook_app, host=host, port=port, **kwargs)
        server = Server(config)
        
        await self.__ready(bot)

        await server.serve()


class Router(Dispatcher):
    
    """
    Роутер для группировки обработчиков событий.
    """
    
    def __init__(self, router_id: str | None = None):
        super().__init__(router_id)


class Event:
    
    """
    Декоратор для регистрации обработчиков событий.
    """
    
    def __init__(self, update_type: UpdateType, router: Dispatcher | Router):
        
        """
        Инициализирует событие-декоратор.

        :param update_type: Тип события (UpdateType).
        :param router: Роутер или диспетчер, в который регистрируется обработчик.
        """
        
        self.update_type = update_type
        self.router = router

    def __call__(self, *args, **kwargs):
        
        """
        Регистрирует функцию как обработчик события.

        :return: Исходная функция.
        """
        
        def decorator(func_event: Callable):
            
            if self.update_type == UpdateType.ON_STARTED:
                self.router.on_started_func = func_event
                
            else:
                self.router.event_handlers.append(
                    Handler(
                        func_event=func_event, 
                        update_type=self.update_type,
                        *args, **kwargs
                    )
                )
            return func_event
            
        return decorator