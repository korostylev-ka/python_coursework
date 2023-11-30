import requests
import configparser
from py_api_vk import MyVKAPI


class MyYandexAPI:
    """ Yandex API
        Copy profile's photos from VK to Yandex Disk
        """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('tokens.ini')
        # check token in file
        try:
            token = config['Token']['yandex_token']
            if len(token) == 0:
                token_input = input('There is no TOKEN in file. Please, enter token here')
                self.token = token_input
            else:
                self.token = token
        except:
            print('Error in yandex token. Check file "tokens.ini"')
            return
        self.vk_api = MyVKAPI()

    def __load_to_yandex_disk(self, count_of_photos):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        photos_list = self.vk_api.save_from_vk_to_pc()
        params = {
            'path': 'VK_Images'
        }
        headers = {
            'Authorization': f'OAuth {self.token}'
        }
        # create folder at Yandex Disk
        requests.put(url, params=params, headers=headers)
        # get numbers of photos needed to upload to Yandex Disk
        count_photos = count_of_photos if count_of_photos <= len(photos_list) else len(photos_list)
        for photo in range(0, count_photos):
            file_name = photos_list[photo].get('file_name')
            params = {
                'path': f'VK_Images/{file_name}',
                'overwrite': True
            }
            headers = {
                'Authorization': f'OAuth {self.token}'
            }
            response = requests.get(f'{url}/upload', params=params, headers=headers)
            url_for_upload = response.json().get('href')
            with open(f'{self.vk_api.DIR_FOR_DOWNLOADED_PHOTOS}/{file_name}', 'rb') as file:
                response = requests.put(url_for_upload, params=params, files={'file': file})

    def copy_from_vk_to_yandex(self):
        count_photos = ''
        while type(count_photos) is not int:
            count_photos_input = input(
                'Enter count of photos you want to upload to Yandex Disk or enter 0 to default(default=5):')
            try:
                count_photos = int(count_photos_input)
            except:
                print('Wrong count of photos. Please try again')
        count_of_photos = 5 if count_photos == 0 else count_photos
        self.__load_to_yandex_disk(count_of_photos)
