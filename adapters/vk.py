from models.user_model import User  # Его класс без изменений

class VKAdapter:
    def __init__(self, token):
        self.user = User(token, None)  # Используем его класс

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
            sex=1 if sex == 'female' else 2  # В его формат
        )
        return [{
            'id': match[0],
            'first_name': match[1],
            'last_name': match[2]
        } for match in self.user.matches]

    def get_photos(self, user_id):
        """Получение фото через его метод"""
        return self.user.get_photos(user_id)