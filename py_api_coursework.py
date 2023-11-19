import json
import os
import requests
import logging

logging.basicConfig(level=logging.DEBUG, filename="py_log.log",filemode="w")
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")


class MyVKAPI:
    """Python coursework API
    Copy profile's photos from VK to Yandex Disk
    """

    API_BASE_URL = 'https://api.vk.com/method'
    VK_TOKEN = 'vk1.a.LFSsbC5E1oED0iLCf96n9i_NxZ_ygwyHy3lyk7qpv1t7-e9N_dbowHQsYgT0KRSINc8y_MvKALJIYjG0sdTJsqkwFxbYgpdS0RY7cz_B4egO9ssIn_USFeK0yJbliIgv8CctCOB0W6s-lm1UonZJoXXhVMlBBU6tcjjTmOdxxYE165nh_UrKVKLHcachJsl7cxe2m9ZOlWRzXot4tst38Q'
    DIR_FOR_DOWNLOADED_PHOTOS = 'vk_downloaded'

    def __init__(self):
        pass

    def __get_common_params(self):
        return {
            'access_token': self.VK_TOKEN,
            'v': '5.154'
        }

    def get_status(self):
        params = self.__get_common_params()
        params.update({'user_id': self.user_id})
        response = requests.get(f'{self.API_BASE_URL}/status.get', params=params)
        return response.json()

    def __get_photos_profile(self, vk_id):
        params = self.__get_common_params()
        params.update(
            {'owner_id': vk_id,
             'album_id': 'profile',
             'extended': '1',
             'photo_sizes': '1'
             })
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            return None

    def __get_photos_list(self, vk_id):
        __photos_list_max_size = []
        __photos = self.__get_photos_profile(vk_id)
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

    def save_from_vk_to_pc(self, vk_id):
        photos_list = self.__get_photos_list(vk_id)
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

    def __load_to_yandex_disk(self, vk_id, token_yandex, count_of_photos):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        photos_list = self.save_from_vk_to_pc(vk_id)
        params = {
            'path': 'VK_Images'
        }
        headers = {
            'Authorization': f'OAuth {token_yandex}'
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
                'Authorization': f'OAuth {token_yandex}'
            }
            response = requests.get(f'{url}/upload', params=params, headers=headers)
            url_for_upload = response.json().get('href')
            with open(f'{self.DIR_FOR_DOWNLOADED_PHOTOS}/{file_name}', 'rb') as file:
                response = requests.put(url_for_upload, params=params, files={'file': file})

    def copy_from_vk_to_yandex(self):
        # input VK id and check that doesn't contains letters
        vk_id = ''
        while type(vk_id) is not int:
            vk_id_input = input('Enter VK id:')
            try:
                vk_id = int(vk_id_input)
            except:
                print('Wrong ID. Please try again')
        yandex_token = input('Enter Yandex token:')
        count_photos = ''
        while type(count_photos) is not int:
            count_photos_input = input('Enter count of photos you want to upload to Yandex Disk or enter 0 to default(default=5):')
            try:
                count_photos = int(count_photos_input)
            except:
                print('Wrong count of photos. Please try again')
        count_of_photos = 5 if count_photos == 0 else count_photos
        self.__load_to_yandex_disk(vk_id, yandex_token, count_of_photos)


if __name__ == '__main__':
    vk = MyVKAPI()
    vk.copy_from_vk_to_yandex()
