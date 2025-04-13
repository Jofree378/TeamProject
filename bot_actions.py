import sqlalchemy
from config import BASE_URL_ACCOUNT
from models.db.DBCrud import DBCrud
from models.user_model import User


def start_search(user: User, users_add_properties: dict = None):
    db = DBCrud()
    user.collect_user_data()

    # Словарь с параметрами пользователя, которые он внес через бот
    if users_add_properties:
        db.create_users_parameters(user_id=users_add_properties.get('user_id'),
                                   age_min=users_add_properties.get('age'),
                                   city=users_add_properties.get('city'),
                                   age_max=users_add_properties.get('age_max'),
                                   sex=users_add_properties.get('sex'))
    else: # Иначе дефолтные параметры
        try:
            db.create_users_parameters(user_id=user.user_id,
                                       age_min=user.age,
                                       city=user.city,
                                       sex=user.sex)
        except sqlalchemy.exc.IntegrityError:
            pass

    # Функция по получения данных из бд
    data = db.get_users_parameters(user.user_id)

    # Поиск по этим данным
    user.get_list_matches(age_min=data.age_min, city=data.city, sex=data.sex, age_max=data.age_max)

    # Добавление найденных данных в бд
    db.delete_all_users_pairs(user.user_id)
    db.add_pairs(user_id=user.user_id, pairs=user.matches)

    # Вывод случайного мэтча
    search_new_match(user)

    # Удаление всех пар для конкретного пользователя
    # db.delete_all_users_pairs(user.user_id)


def search_new_match(user: User):
    db = DBCrud()

    # Получаем кортеж из таблицы Pairs
    match = db.get_match(user_id=user.user_id)

    # Получаем двухуровневый список с фото этого мэтча
    photos = user.get_photos(match[0])

    result_message = {
        'Имя' : match[1],
        'Фамилия' : match[2],
        'Ссылка' : f'{BASE_URL_ACCOUNT}{match[0]}',
        'attachment' : {'one' : photos[0],
                        'two' : photos[1],
                        'three' : photos[2]},
        'pair_id' : match[3]
    }

    return result_message

# Добавление в избранное, вообще это повтор функции из бд, но тоже надо бы ее обдумать
def add_to_favorite(result_message: dict):
    db = DBCrud()
    db.add_favorite_match(result_message=result_message)

# Функция для поиска следующего мэтча, не совсем идеальная - нужно ограничение на количество записей, позже допишу.
def next_match(user: User, result_message: dict):
    db = DBCrud()
    db.delete_row(result_message['pair_id'])

    search_new_match(user=user)
