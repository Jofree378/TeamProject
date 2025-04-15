from vk_api.keyboard import VkKeyboardColor

class MessageHandler:
    def __init__(self, bot):
        self.bot = bot
        self.user_states = {}  # Для хранения состояния диалога

    def handle(self, message):
        user_id = message['from_id']
        text = message['text'].lower()

        # Обработка команд
        if text == 'начать':
            self._handle_start(user_id)
        elif text == 'поиск':
            self._handle_search(user_id)
        elif text == 'избранное':
            self._handle_favorites(user_id)
        elif text == 'помощь':
            self._handle_help(user_id)
        elif self.user_states.get(user_id) == 'await_city':
            self._handle_city_input(user_id, text)
        # Другие состояния и команды...

    def _handle_start(self, user_id):
        """Обработка команды 'начать'"""
        profile = self.bot.vk_client.get_profile(user_id)
        if not profile.get('city'):
            self.user_states[user_id] = 'await_city'
            self.bot.vk.messages.send(
                user_id=user_id,
                message="Укажите ваш город:",
                keyboard=self.bot.keyboard.get_cancel_keyboard(),
                random_id=0
            )
        else:
            self.bot.db.initialize_user(user_id, profile)
            self._send_main_menu(user_id)

    def _handle_search(self, user_id):
        """Обработка команды 'поиск'"""
        criteria = self.bot.db.get_user(user_id)
        matches = self.bot.vk_client.search_users(**criteria)
        
        if matches:
            self.bot.db.cache_matches(user_id, matches)
            self._show_match(user_id, matches[0])
        else:
            self.bot.vk.messages.send(
                user_id=user_id,
                message="Не найдено подходящих анкет",
                keyboard=self.bot.keyboard.get_main_menu(),
                random_id=0
            )

    def _show_match(self, user_id, match):
        """Показ анкеты с клавиатурой действий"""
        photos = self.bot.vk_client.get_photos(match['id'])
        
        self.bot.vk.messages.send(
            user_id=user_id,
            message=f"{match['first_name']} {match['last_name']}\n"
                   f"Ссылка: vk.com/id{match['id']}",
            attachment=','.join(photos),
            keyboard=self.bot.keyboard.get_search_actions(),
            random_id=0
        )

    def _handle_favorites(self, user_id):
        """Показ избранного"""
        favorites = self.bot.db.get_favorites(user_id)
        if not favorites:
            self.bot.vk.messages.send(
                user_id=user_id,
                message="У вас пока нет избранных анкет",
                keyboard=self.bot.keyboard.get_main_menu(),
                random_id=0
            )
            return

        # Отправляем первую анкету из избранного
        self._show_favorite_profile(user_id, favorites[0])

    def _show_favorite_profile(self, user_id, favorite):
        """Показ анкеты из избранного"""
        photos = self.bot.vk_client.get_photos(favorite['match_id'])
        
        self.bot.vk.messages.send(
            user_id=user_id,
            message=f"❤️ Избранное:\n{favorite['first_name']} {favorite['last_name']}",
            attachment=','.join(photos),
            keyboard=self.bot.keyboard.get_favorites_actions(),
            random_id=0
        )

    def _handle_city_input(self, user_id, city):
        """Обработка ввода города"""
        if city.lower() == 'отмена':
            self._send_main_menu(user_id)
            return

        # Сохраняем город и продолжаем регистрацию
        profile = self.bot.vk_client.get_profile(user_id)
        profile['city'] = city
        self.bot.db.initialize_user(user_id, profile)
        
        self._send_main_menu(user_id, f"Город {city} сохранён!")

    def _send_main_menu(self, user_id, additional_message=""):
        """Отправка главного меню"""
        message = "Выберите действие:"
        if additional_message:
            message = f"{additional_message}\n\n{message}"
            
        self.bot.vk.messages.send(
            user_id=user_id,
            message=message,
            keyboard=self.bot.keyboard.get_main_menu(),
            random_id=0
        )

    def _handle_help(self, user_id):
        """Обработка команды помощи"""
        help_text = (
            "📌 Доступные команды:\n"
            "• Поиск - найти новые анкеты\n"
            "• Избранное - просмотреть сохранённые анкеты\n"
            "• Помощь - показать это сообщение\n\n"
            "При поиске:\n"
            "❤️ - добавить в избранное\n"
            "➡️ - следующий профиль\n"
            "✖️ - добавить в чёрный список"
        )
        self.bot.vk.messages.send(
            user_id=user_id,
            message=help_text,
            keyboard=self.bot.keyboard.get_main_menu(),
            random_id=0
        )