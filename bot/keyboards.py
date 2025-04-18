"""
МЕНЕДЖЕР КЛАВИАТУР - ГЕНЕРАЦИЯ КНОПОК

Что содержит:
- Готовые шаблоны клавиатур для всех сценариев
- Унифицированные стили кнопок
- Логику группировки кнопок

Как использовать:
1. Добавить новый метод get_*_keyboard()
2. Вызывать из обработчиков когда нужно

Важно:
- one_time=True - для меню (исчезает после нажатия)
- inline=True - для действий (остается на экране)
- Цвета кнопок соответствуют их назначению
"""

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class KeyboardManager:
    def __init__(self):
        self._keyboard = VkKeyboard()

    @staticmethod
    def get_main_menu():
        """Клавиатура основного меню"""
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Избранное', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('Помощь', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    @staticmethod
    def get_search_actions():
        """Клавиатура при поиске"""
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button('❤️ В избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('➡️ Следующий', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()

    @staticmethod
    def get_favorites_actions():
        """Клавиатура для избранного"""
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button('Написать', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Удалить', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()
    
    @staticmethod
    def get_back_keyboard():
        """Клавиатура с кнопкой возврата"""
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()

    @staticmethod
    def get_favorites_list_keyboard():
        """Клавиатура для списка избранного"""
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()