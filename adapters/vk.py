"""
АДАПТЕР ДЛЯ VK API (обертка для твоего User)

Что делает:
1. Использует твой класс User как черный ящик
2. Преобразует твои структуры данных в наши
3. Обрабатывает все различия в форматах

Особенности:
- get_profile() - возвращает данные в унифицированном формате
- search_users() - конвертирует наши параметры в твой формат
- get_photos() - просто прокси к твоему методу

Если меняешь:
- Сигнатуры методов User - дай знать
- Формат возвращаемых данных - возможно, потребуются правки здесь
"""

from models.user_model import User  

class VKAdapter:
    def __init__(self, token):
        self.user = User(token, None)  

    def get_profile(self, user_id):
        """Получение данных профиля"""
        self.user.user_id = user_id
        self.user.collect_user_data()  # Его метод
        return {
            'age': self.user.age,
            'city': self.user.city,
            'sex': 'female' if self.user.sex == 2 else 'male'
        }

    def search_users(self, age, city, sex):
        """Поиск с конвертацией параметров"""
        self.user.get_list_matches(
            age_min=age,
            city=city,
            sex=1 if sex == 'female' else 2  
        )
        return [{
            'id': match[0],
            'first_name': match[1],
            'last_name': match[2]
        } for match in self.user.matches]

    def get_photos(self, user_id):
        """Получение фото через метод"""
        return self.user.get_photos(user_id)