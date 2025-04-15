import requests
from datetime import datetime


class User:

    def __init__(self, access_token, user_id, version='5.131'):
        self.user_id = user_id
        self.token = access_token
        self.params = {'access_token': self.token, 'v': version}
        self.base_url = 'https://api.vk.com/method/'
        self.age = 0
        self.sex = 0
        self.city = 0
        self.matches = []

    # Получение базовых данных о пользователя для сбора предпочтений
    def collect_user_data(self):
        url = f'{self.base_url}users.get'
        params = {'user_ids': self.user_id, 'fields': 'city,sex,bdate'}
        response = requests.get(url, params={**self.params, **params})
        data = response.json()['response'][0]
        now = datetime.now()
        bdate = datetime.strptime(data['bdate'], "%d.%m.%Y")
        self.age = now.year - bdate.year - ((now.month, now.day) < (bdate.month, bdate.day))
        self.sex = data['sex']
        self.city = data['city']['id']


    # Метод возвращает список строк для поля Attachment в методе message.send. Нужно для прикрепления фото к сообщению
    def get_photos(self, user_id, count: int = 3) -> list:
        url = f'{self.base_url}photos.get'
        params = {'owner_id': user_id, 'count': count, 'album_id':
            'profile', 'extended': 1}
        params.update(self.params)
        response = requests.get(url, params=params)
        result = []
        user_profile_album = response.json()['response']['items']
        for photo in user_profile_album:
            # Тут смотря как сработает вроде с токеном, а вроде и без него
            result.append(f"photo{user_id}_{photo['id']}_{self.token}")
        return result


    # Получаем список всех пользователей подходящих под предпочтения
    def get_list_matches(self, age_min, city, sex, age_max):
        url = f'{self.base_url}users.search'
        params = {'owner_id': self.user_id,
                  'count': 1000,
                  'city': city,
                  'age_from': age_min,
                  'age_to': age_max,
                  'sex': sex,
                  'has_photo': 1
                  }
        params.update(self.params)
        response = requests.get(url, params=params)
        result = []
        pairs = response.json()['response']['items']
        for match in pairs:
            result.append([match['id'], match['first_name'], match['last_name']])
        self.matches = result