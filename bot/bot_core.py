import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from adapters.db import DatabaseAdapter
from adapters.vk import VKAdapter
from bot.handlers import MessageHandler
from bot.keyboards import KeyboardManager
from config import Config


class VKinderBot:
    def __init__(self):
        self.config = Config()
        self.vk = vk_api.VkApi(token=self.config.VK_GROUP_TOKEN)
        self.longpoll = VkBotLongPoll(self.vk, self.config.GROUP_ID)
        self.db = DatabaseAdapter(self.config.DNS)
        self.vk_client = VKAdapter(self.config.VK_USER_TOKEN)
        self.handler = MessageHandler(self)
        self.keyboard = KeyboardManager()
        self.handler = MessageHandler(self)

    def run(self):
        for event in self.longpoll.listen():
            if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
                self.handler.handle(event.message)