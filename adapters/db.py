from models.db.DBCrud import DBCrud  # Его код без изменений
from sqlalchemy import create_engine

class DatabaseAdapter:
    def __init__(self, dsn):
        self.engine = create_engine(dsn)
        self.crud = DBCrud()  # Используем его класс как есть

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
        )  # Фикс: правильное закрытие скобок

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