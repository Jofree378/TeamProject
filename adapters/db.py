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
    def __init__(self, dsn):
        self.engine = create_engine(dsn)
        self.crud = DBCrud()  # Используем твой класс как есть

    def get_user(self, user_id):
        """Конвертация его формата в ваш"""
        params = self.crud.get_users_parameters(user_id)
        return {
            'age': params.age_min,
            'city': params.city['title'] if isinstance(params.city, dict) else params.city,
            'sex': 'female' if params.sex == 2 else 'male'
        }

    def save_match(self, user_id, match_data):
        """Сохранение пары в его формате"""
        self.crud.add_pairs(
            user_id,
            [[match_data['id'], match_data['first_name'], match_data['last_name']]]
        )

    def add_to_favorites(self, pair_id, photos):
        """Добавление в избранное через его метод"""
        self.crud.add_favorite_match({
            'pair_id': pair_id,
            'attachment': {
                'photo1': photos[0],
                'photo2': photos[1],
                'photo3': photos[2]
            }
        })