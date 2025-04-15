import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

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