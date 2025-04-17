"""
АДАПТЕР ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ (обертка для твоего DBCrud)

Как это работает:
1. Берет твой оригинальный DBCrud и добавляет слой совместимости
2. Конвертирует твои форматы данных в наши и обратно
3. Не требует изменений в твоем коде!

Основные методы:
- get_user() - получает параметры пользователя в нашем формате
- save_match() - сохраняет пару в твоем формате
- add_to_favorites() - добавляет в избранное через твой метод

Важно:
- Все SQLAlchemy-специфичные вещи остаются в твоем коде
- Если ты меняешь методы в DBCrud - просто сообщи, я обновлю адаптер
"""

from models.db.DBCrud import DBCrud  # Твой код без изменений
from sqlalchemy import create_engine

class DatabaseAdapter:
    def __init__(self, dns):
        self.engine = create_engine(dns)
        self.crud = DBCrud(self.engine)  # Используем твой класс как есть

    def get_user(self, user_id):
        """Конвертация его формата в ваш"""
        params = self.crud.get_users_parameters(user_id)
        return {
            'age': params.age_min,
            'age_max': params.age_max,
            'city': params.city['title'] if isinstance(params.city, dict) else params.city,
            'sex': params.sex
        }

    def initialize_user(self, user_id, profile: dict):
        """Вставка параметров поиска по дефолт юзера"""
        self.crud.create_users_parameters(user_id, profile)

    def save_match(self, user_id, match_data):
        """Сохранение пары в его формате"""
        self.crud.add_pairs(
            user_id,
            [[match_data['id'], match_data['first_name'], match_data['last_name']]]
        )

    def cache_matches(self, user_id, matches: list):
        """Добавление в кэш базу данных о мэтчах"""
        self.crud.add_pairs(user_id, matches)


    def add_to_favorites(self, pair_id, photos):
        """Добавление в избранное через его метод"""
        self.crud.add_favorite_match(pair_id=pair_id, photos=photos)

    def get_favorites(self, user_id):
        """Получение списка избранных"""
        return [{
            'pair_id': pair.id,
            'first_name': pair.match_name,
            'last_name': pair.match_surname,
            'match_id' : pair.match_id
        } for pair in self.crud.select_favorite(user_id)]

    def get_photos_to_favorites(self, pair_id):
        """Получение фото из БД для большей скорости показа избранных"""
        photos = self.crud.get_photos(pair_id)
        return photos.photo_string


    def next_match(self, user_id, pair_id=None):
        """Выбор случайного мэтча из бд и удаление записи о прошлом, если он не в избранных"""
        if pair_id is not None:
            self.crud.check_for_next_match(pair_id)

        match = self.crud.get_match(user_id=user_id)
        return {'id' : match[0],
                'first_name' : match[1],
                'last_name' : match[2],
                'pair_id' : match[3]
        }