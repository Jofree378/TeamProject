import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UsersParameters(Base):
    __tablename__ = 'users_parameters'

    user_id = sq.Column(sq.Integer, primary_key=True)
    age = sq.Column(sq.Integer, sq.CheckConstraint('age >= 16'), nullable=False)
    age_max = sq.Column(sq.Integer, sq.CheckConstraint('age_max <= 80'))
    city = sq.Column(sq.String(length=60), nullable=False)
    sex = sq.Column(sq.String(length=3), nullable=False)

    sq.CheckConstraint(age_max >= age, name='age_check')


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
