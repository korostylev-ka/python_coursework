from py_api_vk import MyVKAPI
from py_api_yandex import MyYandexAPI

if __name__ == '__main__':
    yandex_api = MyYandexAPI()
    yandex_api.copy_from_vk_to_yandex()

