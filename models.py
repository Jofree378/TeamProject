import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from config import TOKEN_D_VK
from user_func import User
from config import DATABASE, PASSWORD, USER, SUBD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class UsersParameters(Base):
    __tablename__ = 'users_parameters'

    user_id = sq.Column(sq.Integer, primary_key=True)
    age_min = sq.Column(sq.Integer, sq.CheckConstraint('age_min >= 16'), nullable=False)  # Минимальный или дефолт возраст
    age_max = sq.Column(sq.Integer, sq.CheckConstraint('age_max <= 80'))
    city = sq.Column(sq.Integer, nullable=False)
    sex = sq.Column(sq.Integer, sq.CheckConstraint('sex >= 0 and sex <= 2'), nullable=False)

    sq.CheckConstraint(age_max >= age_min, name='age_check')


class Pairs(Base):
    __tablename__ = 'pairs'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users_parameters.user_id'), nullable=False)
    match_id = sq.Column(sq.Integer, nullable=False)
    match_name = sq.Column(sq.String, nullable=False)
    match_surname = sq.Column(sq.String, nullable=False)
    favorite = sq.Column(sq.BOOLEAN, nullable=False, default=False)

    search_pair = relationship(UsersParameters, backref='user_pair')

class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    pair_id = sq.Column(sq.Integer, sq.ForeignKey('pairs.id'), nullable=False)
    photo_id = sq.Column(sq.Integer, nullable=False)

    match_photos = relationship(Pairs, backref='photos')


class DBCrud:

    def __init__(self):
        DNS = f'{SUBD}://{USER}:{PASSWORD}@localhost:5432/{DATABASE}'
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

    # Добавление всех метчей в таблицу пар
    def add_pairs(self, user_id, pairs):
        with self.Session() as session:
            for match in pairs:
                session.add(UsersParameters(user_id=user_id, match_id=match[0], match_name=match[1], match_surname=match[2]))
            session.commit()

    # Добавление флага избранные в таблице пар
    def add_favorite_match(self, user_id, pair_id):
        user = User(TOKEN_D_VK, user_id)
        with self.Session() as session:
            session.query(Pairs).filter(Pairs.id == pair_id).update({'favorite': 1})
            for photo in user.get_photos():
                session.add(Photo(pair_id=pair_id, photo_id=photo))
            session.commit()
