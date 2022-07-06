from typing import List
import requests

from api.models import ItemsBase, OrderBase, ReviewBase, User, UserBase


def get_list_items(item_type: str = None):
    url = 'http://127.0.0.1:8000/items/get_list/{item_type}'.format(item_type=item_type if item_type is not None else '')
    headers = {'accept': 'application/json'}

    result = requests.get(url, headers=headers)
    return result.json()


def get_list_items_popular(item_type: str = None):
    url = 'http://127.0.0.1:8000/items/get_list_popular/{item_type}'.format(item_type=item_type)
    headers = {'accept': 'application/json'}

    result = requests.get(url, headers=headers)
    return result.json()


def get_product(id: int):
    url = 'http://127.0.0.1:8000/items/{id}'.format(id=id)
    headers = {'accept': 'application/json'}

    result = requests.get(url, headers=headers)
    return result.json()


def get_products_by_user(user_id: int, item_type: str ='product')  -> list:
    url = 'http://127.0.0.1:8000/items/get_by_user/{item_type}/{user_id}'.format(item_type=item_type,
        user_id=user_id)
    headers = {'accept': 'application/json'}

    result = requests.get(url, headers=headers)
    return result.json()


def search_product(search: str, item_type: str = 'product') -> list :
    url = 'http://127.0.0.1:8000/items/search/{item_type}/{search}'.format(search=search, item_type=item_type)
    headers = {'accept': 'application/json'}

    result = requests.get(url, headers=headers)
    return result.json()


def create_product(product: ItemsBase):
    url = 'http://127.0.0.1:8000/items/create'

    result = requests.post(url, data=product.json())
    return result.json()


def update_product(id: int, name: str = None, price: float = None, images: str = None, description: str = None) -> dict:
    url = 'http://127.0.0.1:8000/items/update'

    params = {'id': id,
              'name': name,
              'description': description,
              'price': price,
              'images': images}

    result = requests.put(url, params=params)

    return result.json()


def delete_product(id: int):
    url = 'http://127.0.0.1:8000/items/delete/'

    params = {'id': id}

    result = requests.delete(url, params=params)

    return result.json()


def vote_for_product(id: int, rating: int):
    url = 'http://127.0.0.1:8000/items/vote'

    params = {'id': id, 'rating': rating}

    result = requests.put(url, params=params)
    return result.json()


###USERS###

def create_user(user: UserBase):
    url = 'http://127.0.0.1:8000/users/create_user'

    result = requests.post(url, data=user.json())
    return result.text


def get_user(user_id: int):
    url = 'http://127.0.0.1:8000/users/get_user/{user_id}'.format(
        user_id=user_id)
    headers = {'accept': 'application/json'}

    result = requests.get(url, headers=headers)
    return result.json()


def update_user_balance(user_id: int, balance: dict) -> dict:
    url = 'http://127.0.0.1:8000/users/update_balance/'

    params = {}
    params['user_id'] = user_id

    result = requests.put(url, params=params, json=balance)

    return result.json()


def update_user_language(user_id: int, language: str) -> dict:
    url = 'http://127.0.0.1:8000/users/update_language'
    params = {'user_id': user_id, 'language': language}

    result = requests.put(url, params=params)

    return result.json()


def update_user_currency(user_id: int, currency: str) -> dict:
    url = 'http://127.0.0.1:8000/users/update_currency'
    params = {'user_id': user_id, 'currency': currency}

    result = requests.put(url, params=params)

    return result.json()


def get_popular_sellers() -> dict:
    url = 'http://127.0.0.1:8000/users/get_popular_sellers'

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()

def get_orders_volume(user_id: int) -> dict:
    url = 'http://127.0.0.1:8000/users/get_orders_volume/{user_id}'.format(user_id=user_id)

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()


def get_count_of_deals_by_user_id(user_id: int) -> int:
    url = 'http://127.0.0.1:8000/users/count_deals/{user_id}'.format(user_id=user_id)

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()

###Orders###


def create_order(order: OrderBase):
    url = 'http://127.0.0.1:8000/orders/create_order'

    result = requests.post(url, data=order.json())

    return result.json()


def get_order(id: int) -> dict:
    url = 'http://127.0.0.1:8000/orders/get_order/{id}'.format(id=id)
    headers = {'accept': 'application/json'}

    result = requests.get(url, headers=headers)
    return result.json()


def update_order_status(id: int, status: str) -> dict:
    url = 'http://127.0.0.1:8000/orders/update_order_status'

    params = {'id': id, 'status': status}
    result = requests.put(url, params=params)

    return result.json()


def get_orders_by_user_id(user_id: int) -> List[dict]:
    url = 'http://127.0.0.1:8000/orders/get_by_user_list/{user_id}'.format(
        user_id=user_id)

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()


def get_active_orders_by_user_id(user_id: int) -> List[dict]:
    url = 'http://127.0.0.1:8000/orders/get_active_by_user_list/{user_id}'.format(
        user_id=user_id)

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()

def set_application_message_id(order_id: int, seller_message_id: int, buyer_message_id: int):
    url = 'http://127.0.0.1:8000/orders/set_application_message_id'

    params = {'id': order_id, 'seller_message_id': seller_message_id, 'buyer_message_id': buyer_message_id}

    result = requests.put(url, params=params)

    return result.json()

###Currencies###


def get_currencies_list(type: str):
    url = 'http://127.0.0.1:8000/currencies/get_list/{type}'.format(type=type)

    headers = {'accept': 'application/json'}

    result = requests.get(url, headers=headers)
    return result.json()


def get_list_currency_by_symbol(symbol: str):
    url = 'http://127.0.0.1:8000/currencies/get_by_symbol/{symbol}'.format(
        symbol=symbol)
    headers = {'accept': 'application/json'}

    result = requests.get(url, headers=headers)
    return result.json()


###Categories###

def get_list_categories():
    url = 'http://127.0.0.1:8000/categories/get_list'

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()

def get_by_lang_item_type(lang: str, item_type: str):
    url = 'http://127.0.0.1:8000/categories/get_by_lang_item_type/{lang}/{item_type}'.format(lang=lang, item_type=item_type)

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()

def get_category_by_lang_and_id(lang: str, id: int):
    url = 'http://127.0.0.1:8000/categories/get_by_lang_and_id/{lang}/{id}'.format(lang=lang, id=id)

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()


###Reviews###

def get_reviews_for_order(item_id: int) -> List[dict]:
    url = 'http://127.0.0.1:8000/reviews/get_by_order/{item_id}'.format(item_id=item_id)

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()

def get_reviews_for_user(user_id: int) -> List[dict]:
    url = 'http://127.0.0.1:8000/reviews/get_by_user/{user_id}'.format(user_id=user_id)

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()

def get_count_reviews_by_user_id(user_id: int) -> dict:
    url = 'http://127.0.0.1:8000/reviews/get_count/{user_id}'.format(user_id=user_id)

    headers = {'accept': 'application/json'}
    result = requests.get(url, headers=headers)
    return result.json()

def create_review(review: ReviewBase):
    url = 'http://127.0.0.1:8000/reviews/create'

    result = requests.post(url, data=review.json())
    return result.json()

