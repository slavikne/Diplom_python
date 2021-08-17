import requests
from pprint import pprint
from datetime import datetime
import json
import pyprind
class YaUploader:
    # Класс для работы с Яндекс диском
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def upload(self, list_url, name_folder):
        """Метод загружает файлы  на яндекс диск"""
        API_BASE_URL_YA = "https://cloud-api.yandex.net/"
        list_path_on_ya = []
        list_files = []
        bar = pyprind.ProgPercent(len(list_url), title=f'Копирование файлов на Яндекс диск...', track_time=False)
        for url in list_url:
            bar.update()
            res = requests.get('https://cloud-api.yandex.net/v1/disk/resources/files', headers=self.headers)
            lisf_files_on_ya = res.json()['items']
            for file_on_ya in lisf_files_on_ya:
                list_path_on_ya.append(file_on_ya['path'])
        # Проверка на наличие файла
            if f'disk:/{name_folder}/{url["count_likes"]}.jpg' in list_path_on_ya:
                # Загрузка файла на Яндекс диск
                response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=self.headers,
                                 params={'path': f'{name_folder}/{url["count_likes"]}_{url["date_photo"]}.jpg', 'overwrite': 'true',
                                         'url': url['url']})
                requests.get(response.json()['href'], headers=self.headers)
                file_name = f'{url["count_likes"]}_{url["date_photo"]}.jpg'
            else:
                response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=self.headers,
                                 params={'path': f'{name_folder}/{url["count_likes"]}.jpg', 'overwrite': 'true',
                                         'url': url['url']})
                requests.get(response.json()['href'], headers=self.headers)
                file_name = f'{url["count_likes"]}.jpg'
            size = url['size_photo']
            list_files.append({'file_name': file_name, 'size': size})
        with open('data.json', 'w', encoding='utf-8') as file:
            file.write(json.dumps(list_files, ensure_ascii=False))
        print('Файлы загружены на Яндекс диск')

    def create_folder(self):
        """Метод создает папку указанную пользователем на яндекс диске и возвращает имя папки"""
        while True:
            name_folder = input("Введите имя папки: ")
            response = requests.put('https://cloud-api.yandex.net/v1/disk/resources', headers=self.headers,
                        params={'path': name_folder})
            if response.status_code == 409:
                print(f'Папка {name_folder} уже существует, повторите ввод')
                # print(response)
            else:
                print(f'Папка {name_folder} создана')
                break
        return name_folder

class VkDownloader:
    # Класс для работы с Вконтакте
    def __init__(self, token, user_id, count_photo=5):
        self.token = token
        self.user_id = user_id
        self.count_photo = count_photo
        self.params = {
            'owner_id': user_id,
            'count': self.count_photo,
            'extended': 1,
            'album_id': 'profile',
            'access_token': token,
            'v':'5.131'
            }

    def download(self):
        """Метод создает список ссылок  Вконтакте на скачиваемые фото и возвращает этот список"""
        URL = 'https://api.vk.com/method/photos.get'
        list_url_on_img =[]
        res_vk = requests.get(URL, params=self.params)
        info_photos = res_vk.json()['response']['items']
        for photo in info_photos:
            date_photo = datetime.utcfromtimestamp(int(photo['date'])).strftime('%Y-%m-%d')
            count_likes = photo['likes']['count']
            img_url = photo['sizes'][-1]['url']
            size = photo['sizes'][-1]['type']
            list_url_on_img.append({'url': img_url, 'count_likes': count_likes, "date_photo": date_photo, "size_photo": size})
        return list_url_on_img

if __name__ == '__main__':
    with open('token_ya.txt', 'r') as file_object:
        token_ya = file_object.read().strip()
    with open('token_vk.txt', 'r') as file_object:
        token_vk = file_object.read().strip()
    id_user = int(input('Введите id пользователя Вконтакте: '))
    count_ph = int(input('Введите количество скачиваемых фото: '))
    downloder = VkDownloader(token_vk, id_user, count_ph)
    list_url_img = downloder.download()
    uploader = YaUploader(token_ya)
    folder = uploader.create_folder()
    uploader.upload(list_url_img, folder)
