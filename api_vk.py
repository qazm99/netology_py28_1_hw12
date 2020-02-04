import requests
from datetime import datetime
import token_vk
from pprint import pprint

# https://vk.com/eshmargunov id (171691064)

# При создании экземпляра задаем первый обязательный параметр id: int либо screen_name: string
# Второй параметр не обязательный автосинхронизация с сервером ВК при создании класса тип bool
# Далее не обязательные параметры с ключами first_name last_name screen_name у всех тип string
class User_vk:
    # если передали какойнибудь идентефикатор пользователя - то создаем экземпляр
    def __new__(cls, *args, **kwargs):
        for number, argument in enumerate(args):
            if (number == 0) and (isinstance(argument, int) or isinstance(argument, str)):
                return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        self.id = None
        self.screen_name = None
        self.user_data_update = None
        self.first_name = None
        self.last_name = None

        for iteration, argument in enumerate(args):
            # первый параметр id или screen_name
            if iteration == 0:
                # если что-то похоже на id
                if isinstance(argument, int):
                    self.id = argument
                # если что то похоже на имя
                elif isinstance(argument, str):
                    self.screen_name = argument
                # если есть аргументы с ключами - пишем атрибуты пользователя и метку обновления данных
                for key, key_argument in kwargs.items():
                    if isinstance(key_argument, str):
                        if key == 'screen_name':
                            self.screen_name = key_argument
                        elif key == 'first_name':
                            self.first_name = key_argument
                        elif key == 'last_name':
                            self.last_name = key_argument
                    elif isinstance(key_argument, datetime):
                        self.user_data_update = key_argument
            #если есть второй параметр - автосинхронизация True
            elif iteration == 1:
                if isinstance(argument, bool) and argument:
                    #пробуем взять данные пользователя с сайта ВК
                    try:
                        if self.id is not None:
                            new_user_data = get_user_data(self.id)
                        else:
                            new_user_data = get_user_data(self.screen_name)
                        if new_user_data:
                            #print(new_user_data)
                            self.id = new_user_data[0]['id']
                            self.screen_name = new_user_data[0]['screen_name']
                            self.first_name = new_user_data[0]['first_name']
                            self.last_name = new_user_data[0]['last_name']
                            self.user_data_update = datetime.now()
                    except Exception as e:
                        print(f'Не удалось синхронизировать пользователя {self.id} {self.screen_name}: {e}')
    #Вывод ссылки пользователя при обращении через print()
    def __str__(self):
        if self.screen_name is not None:
            return f'Ссылка на страницу {self.first_name} {self.last_name}: https://vk.com/{self.screen_name}'
        else:
            return f'Не найдена ссылка у {self.first_name} {self.last_name}, попробуйте так: https://vk.com/id{self.id}'
    # Перегружаем оператор & для поиска общих друзей у двух пользователей ВК
    def __and__(self, other):
        try:
            if isinstance(other, User_vk):
                print(f'Сейчас поищем  друзей у {self.first_name} и {other.first_name}')
                ids_list_users = list(map(str, get_mutual_friends(self, other)))
                mutal_users_list = []
                for mutal_user in get_user_data(ids_list_users):
                    mutal_users_list.append(User_vk(mutal_user.get('id'), screen_name=mutal_user.get('screen_name'), first_name=mutal_user.get('first_name'), last_name=mutal_user.get('last_name'), user_data_update=datetime.now()))
                print(f'Количество общих друзей {len(mutal_users_list)}')
                return mutal_users_list
        except Exception as e:
            print(f'Не удалось выполнить поиск общих друзей: {e}')

# передаем метод и параметры запроса
def requests_vk(method, params):
    URL = 'https://api.vk.com/method/'
    params['access_token'] = token_vk.token_vk
    params['v'] = '5.103'
    try:
        result_request = requests.get(URL + method, params)
        if result_request.status_code == 200:
            return result_request
        elif result_request.status_code == 404:
            print(f'Неудачная попытка соединения: {result_request.status_code}')
        else:
            print(f'Неудачная попытка соединения: {result_request.status_code}-{result_request.text}')
    except Exception as e:
        print(f'Не удалось получить ответ на запрос от сайта: {e}')

#запрашиваем данные пользователей
def get_user_data(user_id):
    if isinstance(user_id, list):
        user_id_param = ', '.join(user_id)
    elif isinstance(user_id, str) or isinstance(user_id, int):
        user_id_param = user_id
    try:
        return requests_vk('users.get', params={'user_ids': user_id_param, 'fields': 'screen_name'}).json()['response']
    except Exception as e:
        print(f'Не удалось получить данные пользователя {user_id_param}')

#по screen_name ищем id, не используется
# def get_user_id_of_name(screen_name):
#     params = {
#         'user': screen_name,
#     }
#     try:
#         return requests_vk('users.get', params=params).json()['response'][0]['id']
#     except Exception as e:
#         print(f'Не удалось получить id пользователя: {e}')
#по id ищем screen_name, не используется
# def get_user_screen_name(id):
#     return requests_vk('users.get', params={'user_id': id, 'fields': 'screen_name'}).json()['response'][0][
#        'screen_name']

#ищем всех друзей пользователя
def get_all_friends(id):
    return requests_vk('friends.get', params={'user_id': id}).json()['response']['items']

def get_mutual_friends(user_vk1, user_vk2):
    #во множестве id друзей первого пользователя ищем пересечение со множеством id друзей второго пользователя
    ids_mutal_friends = set(get_all_friends(user_vk1.id)).intersection(set((get_all_friends(user_vk2.id))))
    return list(ids_mutal_friends)

#поиск друзей 2 пользователей через апи вк, не используется
# def get_mutual_friends_api_vk(source_uid, target_uid):
#    return requests_vk('friends.getMutual', params={'source_uid': source_uid, 'target_uid': target_uid}).json()


if __name__ == '__main__':
    while True:
        users_sourse_list = []
        print('Сейчас будем пробовать искать общих друзей у двух пользователей ВК ')
        if input('Вы хотите сами ввести пользователей для поиска друзей?(да/нет)').lower() == 'да':
            try:
                users_sourse_list.append(User_vk(input('Введите ид или имя первого пользователя: '), True))
                users_sourse_list.append(User_vk(input('Введите ид или имя второго пользователя: '), True))
            except Exception as e:
                print(f'Некорректные данные пользователя: {e}')
        else:
            pass
            print('Тогда используем предустановленных пользователей')
            #берем двух пользователей, которые являются друзьями в ВК
            users_sourse_list.append(User_vk(171691064, True))
            users_sourse_list.append(User_vk(173110550, True))
            # users_sourse_list.append(User_vk('id46680193', True))
            # users_sourse_list.append(User_vk('mironov1974', True))
        #Печатаем ссылки на их страницы
        try:
            print('Пользователи у которых будем искать общих друзей:')
            for current_user in users_sourse_list:
                print(current_user)
            #Формируем список общих друзей
            users_mutal_list = users_sourse_list[0] & users_sourse_list[1]
            for user in users_mutal_list:
                print(f'{user}')
        except Exception as e:
            print(f'Что то пошло не так: {e}')

        if input('Попробуем еще разок?(да/нет)').lower() != 'да':
            break
    print('Работа программы завершена')
