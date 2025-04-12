import vk_api
from vk_api.longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlalchemy as sq
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import UsersParameters, Pairs, Photo, create_tables
# from config1 import VK_GROUP_TOKEN, VK_USER_TOKEN, GROUP_ID
from config import DATABASE, PASSWORD, USER, SUBD

class VK_Dating_Bot:
    def __init__(self):
        self.group_vk = vk_api.VkApi(token = VK_GROUP_TOKEN)
        self.user_id = vk_api.VkApi()
        self.longpoll = VkBotLongPoll(self.group_vk, GROUP_ID)

        self.engine = create_engine(DNS)
        create_tables(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def run(self):
    # Основной цикл работы бота
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.handle_message(event.message)

    def handle_message(self, message):
        # Обработка входящего сообщения
        user_id = message['from_id']  # ID пользователя
        text = message['text'].lower()  # Текст сообщения в нижнем регистре

        with self.Session() as session:
        
            user = session.query(UsersParameters).filter_by(user_id=user_id).first()

            if text == 'начать':  # Команда старта
                self.send_welcome(user_id)
            elif text == 'поиск':  # Команда поиска
                self.start_search(user_id, session)
            elif text == 'избранное':  # Показать избранное
                self.show_favorites(user_id, session)
            elif not user:  # Если пользователь новый
                self.collect_user_data(user_id, text, session)
            else:  # Обработка других команд
                self.process_search_commands(user_id, text, session)

    def send_welcome(self, user_id):
        # Приветственное сообщение
        keyboard = VkKeyboard()
        keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Избранное', color=VkKeyboardColor.SECONDARY)

        # Получаем имя пользователя
        user_info = self.user_vk.method('users.get', {'user_ids': user_id})[0]
        self.send_message(
            user_id,
            f"Привет, {user_info['first_name']}! Я помогу тебе найти интересных людей.",
            keyboard
        )


