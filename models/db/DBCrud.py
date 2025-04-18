from sqlalchemy.exc import IntegrityError
from models.db.db_model import Base, UsersParameters, Pairs, Photo
from sqlalchemy.orm import sessionmaker
import random


# noinspection PyTypeChecker
class DBCrud:


    def __init__(self, engine):
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)


    def create_users_parameters(self, user_id, profile):
        """Добавление в таблицу данных и предпочтениях пользователя"""
        if not profile.get('age_max'):
            profile['age_max'] = profile['age']

        with self.Session() as session:
            try:
                session.add(UsersParameters(user_id=user_id,
                                            age_min=profile['age'],
                                            age_max=profile['age_max'],
                                            city=profile['city'],
                                            sex=profile['sex']))
                session.commit()
            except IntegrityError:
                session.rollback()

    # Обновление предпочтений пользователя

    def update_users_parameters(self, user_id, age_min=None, city=None, sex=None, age_max=None):
        """Не используется"""

        with self.Session() as session:
            fields = session.query(UsersParameters).filter(UsersParameters.user_id == user_id).one()
            if (age_max and age_max < age_min) or (not age_max and fields.age_max < age_min):
                age_max = age_min
            session.query(UsersParameters).filter(UsersParameters.user_id == user_id).\
             update({'age_min' : age_min if age_min is not None else fields.age_min,
                     'age_max' : age_max if age_max is not None else fields.age_max,
                     'city' : city if city is not None else fields.city,
                     'sex' : sex if sex is not None else fields.sex})
            session.commit()


    def get_users_parameters(self, user_id: int):
        """Возвращает объект с пользовательскими предпочтениями"""
        with self.Session() as session:
            return session.query(UsersParameters).filter(UsersParameters.user_id == user_id).one()


    def add_pairs(self, user_id, pairs):
        """Добавление всех мэтчей в таблицу пар"""
        with self.Session() as session:
            for match in pairs:
                try:
                    session.add(Pairs(user_id=user_id,
                                      match_id=match['id'],
                                      match_name=match['first_name'],
                                      match_surname=match['last_name']))
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    continue


    def add_favorite_match(self, pair_id, photos):
        """Добавление флага избранные в таблице пар и фото избранных с таблицу Photo"""
        with self.Session() as session:
            session.query(Pairs).filter(Pairs.id == pair_id).update({'favorite': 1})
            try:
                session.add(Photo(match_id=pair_id, photo_string=photos))
                session.commit()
            except IntegrityError:
                session.rollback()

    """Новое"""
    def select_favorite(self, user_id: int):
        """Выбор записей с флагом избранное"""
        with self.Session() as session:
            return session.query(Pairs).filter(Pairs.user_id == user_id, Pairs.favorite == True).all()


    def delete_row(self, pair_id):
        """Удаление показанного мэтча"""
        with self.Session() as session:
            session.query(Pairs).filter(Pairs.id == pair_id).delete()
            session.commit()


    # Удаление всех пар для конкретного пользователя
    def delete_all_users_pairs(self, user_id):
        """Не используется"""
        with self.Session() as session:
            session.query(Pairs).filter(Pairs.user_id == user_id).delete()
            session.commit()

    """Новое"""
    def get_match(self, user_id) -> tuple:
        """Выбор следующего пользователя"""
        with self.Session() as session:
            all_matches = session.query(Pairs).filter(Pairs.user_id == user_id).all()
            match = all_matches[random.randint(1, len(all_matches))]
            return match.match_id, match.match_name, match.match_surname, match.id


    def check_for_next_match(self, pair_id):
        """Проверка, что мэтч в избранном и его удаление если нет"""
        with self.Session() as session:
            match = session.query(Pairs).filter(Pairs.id == pair_id).one()
            if not match.favorite:
                self.delete_row(pair_id)


    def get_photos(self, pair_id):
        """Получение фото из таблицы Photo"""
        with self.Session() as session:
            return session.query(Photo).filter(Photo.match_id == pair_id).one()

