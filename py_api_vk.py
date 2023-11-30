import json
import os
import requests
import logging
import configparser

logging.basicConfig(level=logging.DEBUG, filename="py_log.log", filemode="w")
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")


class MyVKAPI:
    """ VK API
    Copy profile's photos from VK
    """

    API_BASE_URL = 'https://api.vk.com/method'
    DIR_FOR_DOWNLOADED_PHOTOS = 'vk_downloaded'

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('tokens.ini')
        try:
            token = config['Token']['vk_token']
            if len(token) == 0:
                token_input = input('There is no TOKEN in file. Please, enter token here')
                self.token = token_input
            else:
                self.token = token
        except:
            print('Error in VK token. Check file "tokens.ini"')
            return
        vk_id_input = input('Enter VK id(digits or named):')
        if vk_id_input.isdigit():
            self.id = vk_id_input
        else:
            self.id = self.__get_digit_id(vk_id_input)

    def __get_digit_id(self, screen_name):
        params = self.__get_common_params()
        params.update({'screen_name': screen_name})
        response = requests.get(f'{self.API_BASE_URL}/utils.resolveScreenName', params=params)
        return response.json().get('response').get('object_id')

    def __get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.154'
        }

    def get_status(self):
        params = self.__get_common_params()
        params.update({'user_id': self.id})
        response = requests.get(f'{self.API_BASE_URL}/status.get', params=params)
        return response.json()

    def __get_photos_profile(self):
        params = self.__get_common_params()
        params.update(
            {'owner_id': self.id,
             'album_id': 'profile',
             'extended': '1',
             'photo_sizes': '1'
             })
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            return None

    def __get_photos_list(self):
        __photos_list_max_size = []
        __photos = self.__get_photos_profile()
        __photos_list = __photos['response']['items']
        for photo in __photos_list:
            date = photo.get('date')
            likes = (photo.get('likes')).get('count')
            photo_type = (photo.get('sizes')[-1]).get('type')
            photo_url = (photo.get('sizes')[-1]).get('url')
            __photos_list_max_size.append({
                'date': date,
                'likes': likes,
                'type': photo_type,
                'url': photo_url
            })
        return __photos_list_max_size

    def save_from_vk_to_pc(self):
        photos_list = self.__get_photos_list()
        photos_info = []
        likes_list = []
        for items in photos_list:
            likes = items.get('likes')
            likes_list.append(likes)
        for items in photos_list:
            likes = items.get('likes')
            date = items.get('date')
            size = items.get('type')
            # if likes count same
            if likes_list.count(likes) > 1:
                file_name = f'{str(likes)}{str(date)}.jpg'
            else:
                file_name = f'{str(likes)}.jpg'
            photos_info.append({
                'file_name': file_name,
                'size': size
            })
            url = items.get('url')
            response = requests.get(url)
            # create folder
            if not os.path.isdir(self.DIR_FOR_DOWNLOADED_PHOTOS):
                os.mkdir(self.DIR_FOR_DOWNLOADED_PHOTOS)
            with open(f'{self.DIR_FOR_DOWNLOADED_PHOTOS}/{file_name}', 'wb') as f:
                f.write(response.content)
        with open('photos_info.json', 'w') as f:
            json.dump(photos_info, f)
        return photos_info
