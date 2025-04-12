from config import DATABASE, PASSWORD, USER, SUBD
from sqlalchemy import create_engine
from models import DBCrud
from user_func import User
from config import TOKEN_D_VK

if __name__ == '__main__':


    db = DBCrud()

    user = User(TOKEN_D_VK, 2223)
    user.collect_user_data()

    # Словарь с параметрами пользователя, которые он внес через бот
    users_add_properties = {}
    if users_add_properties:
        db.create_users_parameters(user_id=users_add_properties['user_id'],
                                   age_min=users_add_properties['age'],
                                   city=users_add_properties['city'],
                                   sex=users_add_properties['sex'])
    # Иначе дефолтные параметры
    else:
        db.create_users_parameters(user_id=user.user_id,
                                   age_min=user.age,
                                   city=user.city,
                                   sex=2)

    # Функция по получения данных из бд

    # Поиск по этим данным

    # Добавление найденных данных в бд