"""
ОБРАБОТЧИКИ СООБЩЕНИЙ - БИЗНЕС-ЛОГИКА

Структура:
- handle() - главный роутер команд
- _handle_* методы - обработка конкретных команд
- _show_* методы - отображение данных

Принцип работы:
1. Получает сообщение от core.py
2. Берет данные из БД/VK через адаптеры
3. Формирует ответ и клавиатуры

Как расширять:
1. Добавить новый _handle_метод для команды
2. Зарегистрировать команду в handle()
"""

class MessageHandler:
    def __init__(self, bot):
        self.bot = bot
        self.user_states = {}  # Для хранения состояния диалога

    def handle(self, message):
        user_id = message['from_id']
        text = message['text'].lower()

        if text == 'начать':
            self._handle_start(user_id)
        elif text == 'поиск':
            self._handle_search(user_id)
        elif text == 'избранное':
            self._handle_favorites(user_id)
        elif text == 'помощь':
            self._handle_help(user_id)
        elif text == 'назад':
            self._send_main_menu(user_id)
        elif text == '➡️ следующий':
            self._handle_next_match(user_id)
        elif text == '❤️ в избранное':
            self._handle_add_to_favorites(user_id)
        elif self.user_states.get(user_id) == 'await_city':
            self._handle_city_input(user_id, text)
        elif self.user_states.get(user_id) == 'viewing_favorites':
            self._handle_favorite_selection(user_id, text)


    def _handle_start(self, user_id):
        """Обработка команды 'начать'"""
        profile = self.bot.vk_client.get_profile(user_id)
        if not profile.get('city'):
            self.user_states[user_id] = 'await_city'
            self.bot.vk.method('messages.send', {
                'user_id': user_id,
                'message': "Укажите ваш город:",
                'keyboard': self.bot.keyboard.get_main_menu(),
                'random_id': 0
            })
        else:
            self.bot.db.initialize_user(user_id, profile)
            self._send_main_menu(user_id)

    def _handle_search(self, user_id):
        """Обработка команды 'поиск'"""
        criteria = self.bot.db.get_user(user_id)
        matches = self.bot.vk_client.search_users(**criteria)

        if matches:
            self.bot.db.cache_matches(user_id, matches)
            match = self.bot.db.next_match(user_id)
            self._show_match(user_id, match)
        else:
            self.bot.vk.method('messages.send', {
                'user_id': user_id,
                'message': "Не найдено подходящих анкет",
                'keyboard': self.bot.keyboard.get_main_menu(),
                'random_id': 0
            })

    def _show_match(self, user_id, match):
        """Показ анкеты с клавиатурой действий"""
        photos = self.bot.vk_client.get_photos(match['id'])
        message = {
            'user_id': user_id,
            'message': f"{match['first_name']} {match['last_name']}\n"
                   f"Ссылка: vk.com/id{match['id']}",
            'attachment' : ','.join(photos),
            'keyboard': self.bot.keyboard.get_search_actions(),
            'random_id': 0
        }
        self.user_states[user_id] = match['pair_id']
        self.user_states['photos'] = ','.join(photos)

        self.bot.vk.method('messages.send', message)

    def _handle_next_match(self, user_id):
        """Переход к следующему мэтчу (обновленная версия)"""
        prev_match = self.user_states.get(user_id)
        if prev_match:
            match = self.bot.db.next_match(user_id, prev_match)
            if match:
                self._show_match(user_id, match)
            else:
                self.bot.vk.method('messages.send', {
                    'user_id': user_id,
                    'message': "Анкеты закончились, попробуйте поискать снова",
                    'keyboard': self.bot.keyboard.get_main_menu(),
                    'random_id': 0
                })
        else:
            self._handle_search(user_id)


    def _handle_add_to_favorites(self, user_id):
        """Добавление в избранное"""
        pair_id = self.user_states[user_id]
        self.bot.db.add_to_favorites(pair_id=pair_id,
                                     photos=self.user_states['photos'])

        match = self.bot.db.next_match(user_id, pair_id)
        self._show_match(user_id, match)



    def _handle_favorites(self, user_id):
        """Обработка команды избранное с показом списка"""
        favorites = self.bot.db.get_favorites(user_id)
        if not favorites:
            self.bot.vk.method('messages.send', {
                'user_id': user_id,
                'message': "У вас пока нет избранных анкет",
                'keyboard': self.bot.keyboard.get_main_menu(),
                'random_id': 0
            })
            return

        self._show_favorites_list(user_id, favorites)
        self.user_states[user_id] = 'viewing_favorites'

    def _show_favorite_profile(self, user_id, favorite):
        """Показ анкеты из избранного"""
        photos = self.bot.db.get_photos_to_favorites(favorite['pair_id'])
        
        self.bot.vk.method('messages.send', {
            'user_id' : user_id,
            'message' : f"❤️ Избранное:\n{favorite['first_name']} {favorite['last_name']}\n"
                        f"Ссылка: vk.com/id{favorite['match_id']}",
            'attachment' : ','.join(photos),
            'keyboard' : self.bot.keyboard.get_favorites_actions(),
            'random_id' : 0
        })

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

        self.bot.vk.method('messages.send', {
            'user_id' : user_id,
            'message' : message,
            'keyboard' : self.bot.keyboard.get_main_menu(),
            'random_id' : 0
        })

    def _show_favorites_list(self, user_id, favorites):
        """Показ списка избранного (новый метод)"""
        message = "❤️ Ваше избранное:\n\n"
        for i, favorite in enumerate(favorites, 1):
            message += f"{i}. {favorite['first_name']} {favorite['last_name']}\n"
            message += f"Ссылка: vk.com/id{favorite['match_id']}\n\n"
        
        self.bot.vk.method('messages.send', {
            'user_id': user_id,
            'message': message,
            'keyboard': self.bot.keyboard.get_favorites_list_keyboard(),
            'random_id': 0
        })

    def _handle_favorite_selection(self, user_id, text):
        """Обработка выбора из списка избранного (новый метод)"""
        try:
            fav_num = int(text)
            favorites = self.bot.db.get_favorites(user_id)
            if 1 <= fav_num <= len(favorites):
                self._show_favorite_profile(user_id, favorites[fav_num-1])
            else:
                self.bot.vk.method('messages.send', {
                    'user_id': user_id,
                    'message': "Неверный номер анкеты",
                    'keyboard': self.bot.keyboard.get_favorites_list_keyboard(),
                    'random_id': 0
                })
        except ValueError:
            self.bot.vk.method('messages.send', {
                'user_id': user_id,
                'message': "Пожалуйста, введите номер анкеты",
                'keyboard': self.bot.keyboard.get_favorites_list_keyboard(),
                'random_id': 0
            })

    def _handle_help(self, user_id):
        """Обработка команды помощи"""
        help_text = (
            "📌 Доступные команды:\n"
            "• Поиск - найти новые анкеты\n"
            "• Избранное - просмотреть сохранённые анкеты\n"
            "• Назад - вернуться в главное меню\n"
            "• Помощь - показать это сообщение\n\n"
            "При поиске:\n"
            "❤️ - добавить в избранное\n"
            "➡️ - следующий профиль\n\n"
            "В избранном:\n"
            "Введите номер анкеты для просмотра"
        )
        self.bot.vk.method('messages.send', {
            'user_id': user_id,
            'message': help_text,
            'keyboard': self.bot.keyboard.get_main_menu(),
            'random_id': 0
        })