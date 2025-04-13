from config import TOKEN_D_VK, DNS
from models.db.db_model import Base, UsersParameters, Pairs, Photo
from models.user_model import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random


# noinspection PyTypeChecker
class DBCrud:


    def __init__(self):
        self.engine = create_engine(DNS)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)


    # def create_tables(engine):
    #     Base.metadata.drop_all(engine)
    #     Base.metadata.create_all(engine)


    # Добавление в таблицу данных и предпочтениях пользователя
    def create_users_parameters(self, user_id, age_min, city, sex, age_max=None):
        if age_max is None:
            age_max = age_min

        # Выбор противоположного пола
        if sex == 2:
            sex = 1
        elif sex == 1:
            sex = 2

        with self.Session() as session:
            session.add(UsersParameters(user_id=user_id, age_min=age_min, age_max=age_max, city=city, sex=sex))
            session.commit()

    # Обновление предпочтений пользователя
    def update_users_parameters(self, user_id, age_min=None, city=None, sex=None, age_max=None):
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

    # Возвращает объект с пользовательскими предпочтениями
    def get_users_parameters(self, user_id: int):
        with self.Session() as session:
            return session.query(UsersParameters).filter(UsersParameters.user_id == user_id).one()

    # Добавление всех мэтчей в таблицу пар
    def add_pairs(self, user_id, pairs):
        with self.Session() as session:
            for match in pairs:
                session.add(Pairs(user_id=user_id, match_id=match[0], match_name=match[1], match_surname=match[2]))
            session.commit()

    # Добавление флага избранные в таблице пар и фото избранных с таблицу Photo
    def add_favorite_match(self, result_message):
        with (self.Session() as session):
            pair_id = result_message['pair_id']
            session.query(Pairs).filter(Pairs.id == pair_id).update({'favorite': 1})
            photos = result_message['attachment']

            for photo in photos.values():
                session.add(Photo(pair_id=pair_id, photo_id=photo.split()[1]))
            session.commit()

    def delete_row(self, pair_id):
        with self.Session() as session:
            session.query(Pairs).filter(Pairs.id == pair_id).delete()
            session.commit()


    # Удаление всех пар для конкретного пользователя
    def delete_all_users_pairs(self, user_id):
        with self.Session() as session:
            session.query(Pairs).filter(Pairs.user_id == user_id).delete()
            session.commit()


    def get_match(self, user_id):
        with self.Session() as session:
            all_matches = session.query(Pairs).filter(Pairs.user_id == user_id).all()
            match = all_matches[random.randint(1, len(all_matches))]
            return match.match_id, match.match_name, match.match_surname, match.id