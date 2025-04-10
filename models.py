import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UsersParameters(Base):
    __tablename__ = 'users_parameters'

    user_id = sq.Column(sq.Integer, primary_key=True)
    age_min = sq.Column(sq.Integer, sq.CheckConstraint('age_min >= 16'), nullable=False)  # Минимальный или дефолт возраст
    age_max = sq.Column(sq.Integer, sq.CheckConstraint('age_max <= 80'))
    city = sq.Column(sq.String(length=60), nullable=False)
    sex = sq.Column(sq.String(length=3), nullable=False)

    sq.CheckConstraint(age_max >= age_min, name='age_check')


class Pairs(Base):
    __tablename__ = 'pairs'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users_parameters.user_id'), nullable=False)
    match_id = sq.Column(sq.Integer, nullable=False)
    favorite = sq.Column(sq.BOOLEAN, nullable=False, default=False)

    search_pair = relationship(UsersParameters, backref='user_pair')

class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    pair_id = sq.Column(sq.Integer, sq.ForeignKey('pairs.id'), nullable=False)
    photo_id = sq.Column(sq.Integer, nullable=False)

    match_photos = relationship(Pairs, backref='photos')


def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


# Добавление в таблицу данных и предпочтениях пользователя
def create_users_parameters(session, user_id, age_min, city, sex, age_max=None):
    if age_max is None:
        age_max = age_min
    session.add(UsersParameters(user_id=user_id, age=age_min, age_max=age_max, city=city, sex=sex))
    session.commit()

# Обновление предпочтений пользователя
def update_users_parameters(session, user_id, age_min=None, city=None, sex=None, age_max=None):
    fields = session.query(UsersParameters).filter(UsersParameters.user_id == user_id).one()
    if age_max < age_min:
        age_max = age_min
    session.query(UsersParameters).filter(UsersParameters.user_id == user_id).\
     update({'age_min' : age_min if age_min is not None else fields.age_min,
             'age_max' : age_max if age_max is not None else fields.age_max,
             'city' : city if city is not None else fields.city,
             'sex' : sex if sex is not None else fields.sex})
    session.commit()
