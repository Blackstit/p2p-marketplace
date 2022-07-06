import os
from unicodedata import category

import api.requests as requests
import telebot
from api.models import Item, ItemsBase, Orders, ReviewBase, User, OrderBase


import bot.markups as markups
import os
import telebot.types
import logging
import bot.config as config
import bot.strings as strings
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


bot = telebot.TeleBot(os.environ.get('TOKEN'), parse_mode='HTML')
logging.basicConfig(level=logging.DEBUG)


@bot.message_handler(commands=['start'])
def start(message):
    user = requests.get_user(message.chat.id)
    if user is None:
        user = User(name=message.chat.first_name,
                    id=message.chat.id)
        msg = bot.send_message(message.chat.id, 'Choose your language',
                               reply_markup=markups.choose_language)
        bot.register_next_step_handler(msg, choose_language, user=user)
    else:
        main_menu(message)


def choose_language(message, user):
    # Над этим еще поработать.
    if user is not None:
        if message.text in config.languages:
            user.language = config.languages[message.text]
            msg = bot.send_message(
                message.chat.id, 'Выберите фиатную валюту', reply_markup=markups.fiat_currencies)
            bot.register_next_step_handler(msg, choose_fiat, user=user)

        else:
            msg = bot.send_message(
                message.chat.id, 'Вы должны выбрать язык из списка', reply_markup=markups.choose_language)
            bot.register_next_step_handler(msg, choose_language, user=user)


def choose_fiat(message, user):
    if message.text == 'Назад':
        main_menu(message)
    else:
        if message.text not in fiat_list():
            msg = bot.send_message(
                message.chat.id, 'Вы должны выбрать валюту из списка', reply_markup=markups.fiat_currencies)
            bot.register_next_step_handler(
                msg, choose_fiat, user=user)
        else:
            if user is not None:
                user.currency = message.text
                requests.create_user(user)
            bot.send_message(message.chat.id, 'Главное меню',
                             reply_markup=markups.main)


@bot.message_handler(regexp='Назад')
@bot.message_handler(regexp='Главное меню')
def main_menu(message):
    bot.send_message(message.chat.id, 'Главное меню',
                     reply_markup=markups.main)


@bot.message_handler(regexp='Маркет')
def market(message):
    bot.send_message(message.chat.id, 'Маркет', reply_markup=markups.market)


@bot.callback_query_handler(lambda c: 'show' in c.data and 'seller' not in c.data)
def show_item(c):
    item_id = c.data.split('_')[1]

    config.show_item(item_id=item_id, bot=bot,
                     message=c.message, show_edit=('my' in c.data))


@bot.message_handler(func=lambda message: 'Товары' == message.text)
@bot.message_handler(func=lambda message: 'Услуги' == message.text)
@bot.message_handler(func=lambda message: 'Задания' == message.text)
@bot.callback_query_handler(lambda c: 'product_list' in c.data)
@bot.callback_query_handler(lambda c: 'service_list' in c.data)
@bot.callback_query_handler(lambda c: 'task_list' in c.data)
def products(message=None, id=0):
    if type(message) is telebot.types.Message:
        item_type = strings.item_types[message.text]

    else:
        c = message
        message = c.message
        id = int(c.data.split('list_')[1])

        item_type = c.data.split('_list')[0]
        bot.delete_message(message.chat.id, message.message_id)

    markup_item_type = strings.item_type_genitive[item_type]

    markup_text = 'Поиск {item_type}'.format(item_type=markup_item_type)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(markup_text)
    markup.add('Назад')

    bot.send_message(message.chat.id, 'Здесь находятся популярные {}'.format(
        message.text.lower()), reply_markup=markup)
    config.list_items(bot=bot, message=message, text='Вас может заинтересовать',
                      request_function=requests.get_list_items_popular, c_data="{item_type}_list".format(item_type=item_type), id=id, item_type=item_type)


@bot.callback_query_handler(lambda c: 'add' in c.data)
def create_product(c):

    user = requests.get_user(c.message.chat.id)

    item_type = c.data.split('_')[1]  # Тип товара
    product = ItemsBase(creator_id=c.message.chat.id, type=item_type)

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    print(user)
    categories = requests.get_by_lang_item_type(
        lang=user['language'], item_type=item_type)

    markup.add(*list(categories.keys()))

    item_type = strings.item_type_genitive[product.type]

    msg = bot.send_message(c.message.chat.id, 'Выберите категорию {item_type}'.format(
        item_type=item_type), reply_markup=markup)

    bot.register_next_step_handler(
        msg, create_product_name, product=product, markup=markup, categories=categories)


def create_product_name(message, markup, categories, product: ItemsBase):
    if message.text not in list(categories.keys()):

        msg = bot.send_message(message.chat.id, 'Вы должны выбрать категорию из списка',
                               reply_markup=markup)
        bot.register_next_step_handler(
            msg, create_product_name, product=product, markup=markup, categories=categories)
    else:
        product.category = categories[message.text]

        item_type = strings.item_type_genitive[product.type]

        msg = bot.send_message(
            message.chat.id, 'Введите название {item_type}'.format(item_type=item_type))
        bot.register_next_step_handler(
            msg, create_product_desc, product=product)


def create_product_desc(message, product: ItemsBase):
    product.name = message.text

    item_type = strings.item_type_genitive[product.type]

    msg = bot.send_message(
        message.chat.id, 'Введите описание {item_type}'.format(item_type=item_type))
    bot.register_next_step_handler(
        msg, create_product_currency, product=product)


def create_product_currency(message, product: ItemsBase):
    if len(message.text) > 1000:
        msg = bot.send_message(
            message.chat.id, 'Описание не должно быть больше 1000 символов')
        bot.register_next_step_handler(
            msg, create_product_currency, product=product)
    product.description = message.text

    msg = bot.send_message(
        message.chat.id, 'Выберите валюту из списка', reply_markup=markups.cryptocurrencies)
    bot.register_next_step_handler(msg, create_product_price, product=product)


def create_product_price(message, product: ItemsBase):
    if message.text == 'Назад':
        start(message)
    else:
        if message.text not in [i['symbol'] for i in requests.get_currencies_list('crypto')]:
            msg = bot.send_message(
                message.chat.id, 'Вы должны выбрать валюту из списка', reply_markup=markups.cryptocurrencies)
            bot.register_next_step_handler(
                msg, create_product_price, product=product)
        else:
            product.currency = message.text

            item_type = strings.item_type_genitive[product.type]

            msg = bot.send_message(
                message.chat.id, 'Введите цену {item_type}'.format(item_type=item_type), reply_markup=markups.empty_markup)
            bot.register_next_step_handler(
                msg, create_product_image, product=product)


def create_product_image(message, product: ItemsBase):
    try:
        product.price = float(message.text)

        if product.price < 0 or product.price > 1000000:
            msg = bot.send_message(
                message.chat.id, 'Цена должна быть в пределах от 0 до 1000000')
            bot.register_next_step_handler(
                msg, create_product_image, product=product)
        else:
            item_type = strings.item_type_genitive[product.type]
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Пропустить')
            msg = bot.send_message(
                message.chat.id, 'Отправьте изображение для {item_type}'.format(item_type=item_type), reply_markup=markup)
            bot.register_next_step_handler(
                msg, create_product_finish, product=product)
    except:
        msg = bot.send_message(message.chat.id, 'Вы должны ввести число')
        bot.register_next_step_handler(
            msg, create_product_image, product=product)


def create_product_finish(message, product: ItemsBase):
    try:
        if message.text == 'Пропустить':
            product.images = None
        else:
            product.images = message.photo[0].file_id

        item = requests.create_product(product)

        item_type = strings.item_type_nominative[product.type]

        text = '{item_type} успешно создан' + 'а' * (item['type'] != 'Товар')

        bot.send_message(message.chat.id, text.format(item_type=item_type),
                         reply_markup=markups.main)
        config.show_item(bot=bot, message=message,
                         item_id=item['id'], show_edit=True)
    except:
        msg = bot.send_message(
            message.chat.id, 'Произошла ошибка, вы должны отправить фото. попробуйте еще раз')
        bot.register_next_step_handler(
            msg, create_product_finish, product=product)


@bot.message_handler(regexp='Поиск товара')
@bot.message_handler(regexp='Поиск услуги')
@bot.message_handler(regexp='Поиск задания')
@bot.callback_query_handler(lambda message: 'search' in message.data)
def search_product(message):
    if type(message) is telebot.types.Message:
        item_type = strings.item_types[message.text.split(' ')[1]]
    else:
        c = message
        message = c.message
        item_type = c.data.split('_')[1]

    item_type_text = strings.item_type_genitive[item_type]
    msg = bot.send_message(message.chat.id, 'Введите название {item_type}'.format(
        item_type=item_type_text))
    bot.register_next_step_handler(msg, find_product, item_type=item_type)


@bot.callback_query_handler(lambda c: 'find' in c.data)
def find_product(message, item_type='product'):
    sort_key = None
    if type(message) is not telebot.types.Message:

        c = message
        message = c.message

        item_type = c.data.split('_')[1]
        if 'price' in c.data:
            sort_key = 'price'

        if 'category' in c.data:
            sort_key = 'category_' + c.data.split('category_')[1]

        id = c.data.split('_')[2]
        search = message.text.split('запросу ')[1]
        bot.delete_message(message.chat.id, message.message_id)
    else:
        id = 0
        search = message.text

    config.list_items(bot=bot, message=message, text='Нашли для вас по запросу {search}'.format(search=search),
                      request_function=requests.search_product,  id=id, c_data='find', sort_key=sort_key, item_type=item_type, search=search)


@bot.callback_query_handler(lambda c: 'category' in c.data)
def choose_category_for_search(c):
    item_type = c.data.split('_')[1]
    user = requests.get_user(c.from_user.id)

    categories = requests.get_by_lang_item_type(
        lang=user['language'], item_type=item_type)

    markup = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(category, callback_data='find_{item_type}_category_{category}'.format(
        item_type=item_type, category=category)) for category in categories]
    markup.add(*buttons)

    bot.edit_message_text('Выберите категорию {}'.format(strings.item_type_genitive[item_type], c. message.text.split('запросу ')[1]),
                          c.message.chat.id,  c.message.id, reply_markup=markup)


@bot.callback_query_handler(lambda c: 'buy' in c.data)
def buy_product(c):
    # callback buy_id
    product_id = int(c.data.split('_')[1])
    product = Item(**requests.get_product(product_id))

    user = User(**requests.get_user(c.message.chat.id))

    orders = [i for i in requests.get_orders_by_user_id(user_id=user.id) if i['buyer'] == user.id and i['seller'] == product.creator_id and i['status'] not in ('finished', 'closed')]

    if len(orders) > 2:
        bot.send_message(c.message.chat.id, 'Вы не можете отправить более 2х заявок продавцу одновременно') 

    if user.balance is not None:
        if product.currency in user.balance:
            if user.balance[product.currency] < product.price:
                bot.send_message(c.message.chat.id,
                                 'У вас недостаточный баланс')
            else:
                order = OrderBase(
                    buyer=c.message.chat.id, seller=product.creator_id, ad_type='product', ad_id=product.id, price=product.price, currency=product.currency, seller_application_message_id=None)
                print('order is', order.json())
                order = requests.create_order(order)
                order = Orders(**order)

                buyer_markup = InlineKeyboardMarkup()
                buyer_markup.add(InlineKeyboardButton('Отменить сделку', callback_data='cancel_order_{}'.format(order.id)))

                buyer_msg = bot.send_message(
                    c.message.chat.id, 'Заявка на покупку отправлена продавцу. Средства на вашем счете заморожены до окончания сделки', reply_markup=buyer_markup)

                new_balance = {
                    product.currency: user.balance[product.currency] - product.price}
                requests.update_user_balance(c.message.chat.id, new_balance)

                

                markup = InlineKeyboardMarkup().add(InlineKeyboardButton('Принять', callback_data='accept{}'.format(
                    order.id)), InlineKeyboardButton('Отклонить', callback_data='reject{}'.format(order.id)))

                msg = bot.send_message(product.creator_id, 'Заявка на покупку {name} за {price} {currency}'.format(
                    name=product.name, price=product.price, currency=product.currency), reply_markup=markup)

                requests.set_application_message_id(order.id, msg.message_id, buyer_msg.message_id)
        else:
            bot.send_message(c.message.chat.id, 'У вас недостаточный баланс')

    else:
        bot.send_message(c.message.chat.id, 'У вас недостаточный баланс')

    bot.answer_callback_query(c.id)


@bot.callback_query_handler(lambda c: 'cancel_order' in c.data)
def cancel_order_by_buyer(c):
    order_id = int(c.data.split('_')[2])
    order = requests.get_order(order_id)
    order = Orders(**order)
    ###return balance to buyer
    user = requests.get_user(c.message.chat.id)
    user = User(**user)
    new_balance = {order.currency: user.balance[order.currency] + order.price}
    requests.update_user_balance(c.message.chat.id, new_balance)

    ###set order status closed
    requests.update_order_status(order_id, status='closed')

    ###send message to seller
    bot.edit_message_text('Заявка отменена покупателем', order.seller, order.seller_application_message_id, reply_markup=None)

    ###send message to buyer
    bot.edit_message_text('Заявка отменена.', order.buyer, order.buyer_application_message_id, reply_markup=None)

    bot.answer_callback_query(c.id)

@bot.callback_query_handler(lambda c: 'accept' in c.data)
def accept_order(c):
    order_id = c.data.split('accept')[1]
    order = requests.get_order(order_id)

    requests.update_order_status(order_id, 'accepted')

    ###edit buyer message application
    bot.edit_message_text('Заявка принята', order['buyer'], order['buyer_application_message_id'], reply_markup=None)

    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(
        'Отправить данные', callback_data='send_item_data{}'.format(order['id'])))

    bot.edit_message_text('Сделка создана. Отправьте покупателю данные цифрового товара.',
                          order['seller'], c.message.id, reply_markup=markup)
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(lambda c: 'send_item_data' in c.data)
def send_item_data(c):
    order_id = int(c.data.split('data')[1])
    order = requests.get_order(order_id)

    msg = bot.edit_message_text(
        'Введите данные цифрового товара', c.message.chat.id, c.message.id)

    bot.register_next_step_handler(msg, receive_item_data, order=order)
    bot.answer_callback_query(c.id)


def receive_item_data(message, order: dict):
    requests.update_order_status(order['id'], 'finished')

    text = 'Данные цифрового товара по сделке {}:\n{}'.format(
        order['id'], message.text)

    contact_markup = InlineKeyboardMarkup()
    contact_markup.add(InlineKeyboardButton(
        'Написать продавцу', callback_data='contact_seller{}'.format(order['id'])))

    bot.send_message(order['buyer'], text, reply_markup=contact_markup)

    rate_markup = InlineKeyboardMarkup()
    rate_markup.add(
        *[InlineKeyboardButton(i, callback_data='rate{}item{}'.format(i, order['ad_id'])) for i in range(1, 6)])
    bot.send_message(order['buyer'], 'Оцените работу продавца',
                     reply_markup=rate_markup)

    item = requests.get_product(order['ad_id'])
    seller = requests.get_user(order['seller'])

    new_seller_balance = {
        item['currency']: seller['balance'][item['currency']] + item['price']}

    requests.update_user_balance(order['seller'], new_seller_balance)
    bot.send_message(
        order['seller'], 'Данные отправлены покупателю. Ваш счет пополнен.', reply_markup=markups.empty_markup)


@bot.callback_query_handler(lambda c: 'rate' in c.data)
def rate_item(c):
    rating = c.data.split('rate')[1].split('item')[0]
    item_id = c.data.split('item')[1]

    item = requests.vote_for_product(item_id, rating)

    msg = bot.edit_message_text('Напишите отзыв о продавце',
                                c.message.chat.id, c.message.id)
    bot.register_next_step_handler(msg, write_review, item=item, rating=rating)


def write_review(message, item: dict, rating: int):
    review = ReviewBase(
        item_id=item['id'], user_id=message.chat.id, text=message.text, rating=rating, seller_id=item['creator_id'])

    requests.create_review(review)

    bot.send_message(message.chat.id, 'Отзыв отправлен продавцу')

    bot.send_message(item['creator_id'],
                     'Отзыв от покупателя:\n{}'.format(message.text))


@bot.callback_query_handler(lambda c: 'contact' in c.data)
def contact_to_seller(c):
    if 'seller' in c.data:
        user_type = 'seller'
        text = 'Напишите сообщение для продавца'
    else:
        user_type = 'buyer'
        'Напишите сообщение для покупателя'
    order_id = int(c.data.split('seller')[1])
    order = requests.get_order(order_id)

    msg = bot.send_message(
        c.message.chat.id, text, reply_markup=markups.back)

    bot.register_next_step_handler(
        msg, send_message_to_seller, order=order, user_type=user_type)


def send_message_to_seller(message, order, user_type: str):
    bot.send_message(
        order['seller'], 'Вы получили сообщение по сделке {}'.format(order['id']), reply_markup=markups.main)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Ответить', callback_data='contact_{user_type}{order_id}'.format(
        user_type=user_type, order_id=order['id'])))
    bot.copy_message(order['seller'], message.chat.id,
                     message.id, reply_markup=markup)


@bot.callback_query_handler(lambda c: 'reject' in c.data)
def reject(c):
    """Get item id and return crypto to buyer"""
    order_id = c.data.split('reject')[1]
    order = requests.get_order(order_id)

    buyer = requests.get_user(order['buyer'])

    new_buyer_balance = {
        order['currency']: buyer['balance'][order['currency']] + order['price']}

    requests.update_user_balance(
        user_id=order['buyer'], balance=new_buyer_balance)

    bot.edit_message_text('Вы отказались от сделки.',
                          c.message.chat.id, c.message.id)
    bot.send_message(
        order['buyer'], 'Продавец отказался от сделки. Ваш счет пополнен.')

    requests.update_order_status(id=order['id'], status='rejected')


@bot.message_handler(regexp='Профиль')
def profile(message):
    user = requests.get_user(message.chat.id)
    items = requests.get_products_by_user(message.chat.id, item_type='product')
    # sum of requests get products by user where item types are product service and task
    # В будущем обновить апи
    sum_items = len(requests.get_products_by_user(message.chat.id, item_type='product')) + len(requests.get_products_by_user(
        message.chat.id, item_type='service')) + len(requests.get_products_by_user(message.chat.id, item_type='task'))
    balance = str(user['balance']).translate({ord(c): None for c in '{\'}'}).replace(
        ', ', '\n') if user['balance'] is not None else 'Нет данных'

    full_ballance = config.get_full_balance(message.chat.id)

    orders_volume = requests.get_orders_volume(message.chat.id)

    orders_count = len( [ i for i in requests.get_orders_by_user_id(message.chat.id) if i['status'] == 'finished'])


    text = """<b>Профиль</b>

Никнейм {name}

{full_ballance}
{balance}

Мои товары {items}
Количество сделок {orders_count}
Всего заработано: {received} {fiat}
Всего потрачено: {spent} {fiat}
Рейтинг {rating}
{reviews}
    """.format(name=user['name'], full_ballance=full_ballance, balance=balance, items=sum_items, rating=user['rating'], received=orders_volume['received'], spent=orders_volume['spent'], reviews=reviews_count(message.chat.id), orders_count=orders_count, fiat=user['currency'])

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Пополнить баланс', callback_data='deposit_balance'),
               InlineKeyboardButton('Вывести деньги', callback_data='withdraw_balance'))
    markup.add(InlineKeyboardButton(
        'Мои отзывы', callback_data='reviews{}id0'.format(message.chat.id)))
    markup.add(InlineKeyboardButton('Мои товары', callback_data='itemsection_product'),
               InlineKeyboardButton(
                   'Мои услуги', callback_data='itemsection_service'),
               InlineKeyboardButton('Мои задания', callback_data='itemsection_task'), row_width=3)

    markup.add(InlineKeyboardButton('Мои сделки', callback_data='dealsection'))

    bot.send_message(message.chat.id, text,
                     reply_markup=markup)


@bot.callback_query_handler(lambda c: 'itemsection' in c.data)
def my_products(c):
    item_type = c.data.split('_')[1]

    products = requests.get_products_by_user(
        c.message.chat.id, item_type=item_type)

    item_type_text = strings.item_type_genitive_plural[item_type]

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Список {item_type}'.format(
        item_type=item_type_text), callback_data='mylist_{item_type}_0'.format(item_type=item_type)))
    markup.add(InlineKeyboardButton('Добавить {item_type}'.format(
        item_type=item_type_text), callback_data='add_{item_type}'.format(item_type=item_type)))

    bot.send_message(c.message.chat.id, 'У вас {count} {item_type}'.format(
        count=len(products), item_type=item_type_text), reply_markup=markup)


@bot.callback_query_handler(lambda c: 'mylist' in c.data)
def my_products_list(message, id=0):

    if type(message) is not telebot.types.Message:
        c = message
        message = c.message

        item_type = c.data.split('_')[1]
        id = int(c.data.split('_')[2])

        bot.delete_message(message.chat.id, message.message_id)

    config.list_items(bot=bot, message=message, text='Ваши {item_type}'.format(item_type={'product': 'товары', 'service': 'услуги', 'task': 'задания'}[item_type]),
                      request_function=requests.get_products_by_user, c_data='mylist', id=id,  user_id=message.chat.id, item_type=item_type)


@bot.callback_query_handler(lambda c: 'edit_item' in c.data)
def edit_item(c):

    item_id = int(c.data.split('item')[1].split('_')[0])
    item = requests.get_product(item_id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Изменить название',
               callback_data='edit_name{}'.format(item['id'])))
    markup.add(InlineKeyboardButton('Изменить описание',
               callback_data='edit_desc{}'.format(item['id'])))
    markup.add(InlineKeyboardButton('Изменить цену',
               callback_data='edit_price{}'.format(item['id'])))
    markup.add(InlineKeyboardButton(
        'Удалить', callback_data='delete_item{}'.format(item['id'])))

    bot.edit_message_caption(
        c.message.caption, c.message.chat.id, c.message.id, reply_markup=markup)


@bot.callback_query_handler(lambda c: 'edit_name' in c.data)
def edit_name(c):

    item_id = int(c.data.split('name')[1])

    item_type = requests.get_product(item_id)['type']
    item_type = strings.item_type_genitive[item_type]

    msg = bot.send_message(
        c.message.chat.id, 'Введите новое название {item_type}'.format(item_type=item_type))

    bot.register_next_step_handler(msg, submit_edit_name, item_id=item_id, c=c)

    bot.answer_callback_query(c.id)


def submit_edit_name(message, item_id: int, c):

    item = requests.update_product(id=item_id, name=message.text)
    item = Item(**item)

    item_type = {'product': 'Товар',
                 'service': 'Услуга', 'task': 'Задание'}[item.type]

    bot.send_message(message.chat.id, 'Название успешно изменено')
    text = strings.item_text
    bot.edit_message_caption(text.format(
        product=item, item_type=item_type), c.message.chat.id, c.message.id, reply_markup=c.message.reply_markup)


@bot.callback_query_handler(lambda c: 'edit_desc' in c.data)
def edit_description(c):

    item_id = int(c.data.split('desc')[1])

    item_type = requests.get_product(item_id)['type']
    item_type = strings.item_type_genitive[item_type]

    msg = bot.send_message(
        c.message.chat.id, 'Введите новое описание {item_type}'.format(item_type=item_type))

    bot.register_next_step_handler(
        msg, submit_edit_description, item_id=item_id, c=c)

    bot.answer_callback_query(c.id)


def submit_edit_description(message, item_id: int, c):

    item = requests.update_product(id=item_id, description=message.text)
    item = Item(**item)

    item_type = strings.item_type_nominative[item.type]

    bot.send_message(message.chat.id, 'Описание успешно изменено')
    text = strings.item_text
    bot.edit_message_caption(text.format(
        product=item, item_type=item_type), c.message.chat.id, c.message.id, reply_markup=c.message.reply_markup)


@bot.callback_query_handler(lambda c: 'edit_price' in c.data)
def edit_price(c):

    item_id = int(c.data.split('price')[1])
    msg = bot.send_message(c.message.chat.id, 'Введите новую цену')

    bot.register_next_step_handler(
        msg, submit_edit_price, item_id=item_id, c=c)

    bot.answer_callback_query(c.id)


def submit_edit_price(message, item_id: int, c):
    try:
        price = float(message.text)

        item = requests.update_product(id=item_id, price=price)
        item = Item(**item)
        item_type = strings.item_type_nominative[item.type]

        bot.send_message(message.chat.id, 'Цена успешно изменена')
        text = strings.item_text
        bot.edit_message_caption(text.format(
            product=item, item_type=item_type), c.message.chat.id, c.message.id, reply_markup=c.message.reply_markup)
    except:
        msg = bot.send_message(
            c.message.chat.id, 'Ошибка. Вы должны ввести число.')
        bot.register_next_step_handler(
            msg, submit_edit_price, item_id=item_id, c=c)


@bot.callback_query_handler(lambda c: 'dealsection' in c.data)
def send_message(c):
    orders = requests.get_orders_by_user_id(c.message.chat.id)

    text = 'У вас {}  сделок'.format(len(orders))

    bot.send_message(c.message.chat.id, text, reply_markup=markups.my_orders)
    bot.answer_callback_query(c.id)


@bot.message_handler(regexp='История сделок')
def orders_history(message):
    text = 'Список ваших сделок: \n'
    orders = requests.get_orders_by_user_id(message.chat.id)

    if len(orders) > 0:
        csv_file = open(
            'bot/csv/orders_{user_id}.csv'.format(user_id=message.chat.id), mode='x')

        csv_file.write(config.get_csv(orders))

        csv_file.close()

        csv_file = open(
            'bot/csv/orders_{user_id}.csv'.format(user_id=message.chat.id), mode='r')

        bot.send_document(message.chat.id, csv_file)

        csv_file.close()

        os.remove(
            'bot/csv/orders_{user_id}.csv'.format(user_id=message.chat.id))
    else:
        bot.send_message(message.chat.id, 'У вас нет сделок')


@bot.message_handler(regexp='Активные сделки')
def active_orders_history(message):
    text = 'Список ваших активных сделок: \n'
    orders = requests.get_active_orders_by_user_id(message.chat.id)

    for order in orders:
        print(order)
        text += 'Сделка №{}\n\n'.format(order['id'])

    bot.send_message(message.chat.id, text)
    bot.send_message(
        message.chat.id, 'Необходимо дополнить в тз, что именно здесь должно быть')


@bot.callback_query_handler(lambda c: 'delete_item' in c.data)
def delete_item(c):
    item_id = int(c.data.split('item')[1])

    item_type = requests.get_product(item_id)['type']

    item_type = strings.item_type_nominative[item_type]

    text = "{item_type} успешно удален" + 'а' * (item_type != 'Товар')

    requests.delete_product(item_id)

    bot.delete_message(c.message.chat.id, c.message.id)
    bot.send_message(c.message.chat.id, text)


@bot.message_handler(regexp='Пополнить баланс')
@bot.callback_query_handler(lambda c: 'deposit_balance' in c.data)
def deposit(message):
    if type(message) is not telebot.types.Message:
        message = message.message

    user = requests.get_user(message.chat.id)
    text = 'Ваш баланс:\n{balance}'.format(balance=str(user['balance']).translate(
        {ord(c): None for c in '{\'}'}).replace(', ', '\n'))
    bot.send_message(message.chat.id, text, reply_markup=markups.deposit)


@bot.callback_query_handler(lambda c: 'deposit' in c.data)
def show_deposit_address(c):
    currency_symbol = c.data.split('_')[1]
    currency = requests.get_list_currency_by_symbol(currency_symbol)
    print(currency)
    text = 'Адрес для пополнения кошелька:\n<code>{}</code>\nКоммент: {}'.format(
        currency['address'], c.message.chat.id)

    bot.send_message(c.message.chat.id, text)

    bot.answer_callback_query(c.id)


@bot.message_handler(regexp='Селлеры')
def sellers(message):
    text = 'Селлеры'

    config.list_items(bot=bot, message=message,
                      request_function=requests.get_popular_sellers, text=text, c_data='seller')


@bot.callback_query_handler(lambda c: 'show_seller' in c.data)
def show_seller(c):
    # Show all seller's data

    seller_id = int(c.data.split('seller')[1])

    reviews = requests.get_reviews_for_user(seller_id)

    seller = requests.get_user(seller_id)
    count_products = len(requests.get_products_by_user(seller['id']))
    text = 'Информация о селлере:\nНикнейм: {name}\nРейтинг: {rating}\nКоличество товаров: {count_products}'.format(
        name=seller['name'], rating=seller['rating'], count_products=count_products)

    if len(reviews) > 0:
        text += reviews_count(seller_id)
        text += '\nПоследний отзыв о селлере:\n{}'.format(reviews[-1]['text'])
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Посмотреть отзывы',
                   callback_data='reviews{}id{}'.format(seller_id, 0)))
        bot.send_message(c.message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(c.message.chat.id, text, reply_markup=markups.market)

    bot.answer_callback_query(c.id)


def reviews_count(seller_id):
    reviews_count = requests.get_count_reviews_by_user_id(seller_id)
    text = '\nОтзывы: ☺ ({positive}) ☹ ({negative})'.format(
        positive=reviews_count['positive'], negative=reviews_count['negative'])
    return text


@bot.callback_query_handler(lambda c: 'reviews' in c.data)
def show_reviews(c):
    # Show reviews by seller id, c.data format is reviews{seller_id}id{page_id}
    seller_id = int(c.data.split('reviews')[1].split('id')[0])
    page_id = int(c.data.split('id')[1])

    reviews = requests.get_reviews_for_user(seller_id)

    seller = requests.get_user(seller_id)

    print(seller)
    text = 'Отзывы о селлере {seller_name}:\n'.format(
        seller_name=seller['name'])

    text += reviews[page_id]['text'] if len(reviews) > 0 else 'Нет отзывов'

    markup = InlineKeyboardMarkup()

    if page_id < len(reviews) - 1:

        markup.add(InlineKeyboardButton('Следующий отзыв',
                   callback_data='reviews{}id{}'.format(seller_id, page_id + 1)))

    if page_id > 0:

        markup.add(InlineKeyboardButton('Предыдущий отзыв',
                   callback_data='reviews{}id{}'.format(seller_id, page_id - 1)))

    bot.edit_message_text(text,  c.message.chat.id,
                          c.message.id, reply_markup=markup)

    bot.answer_callback_query(c.id)


@bot.message_handler(regexp="Настройки")
def settings(message):
    bot.send_message(message.chat.id, 'Настройки',
                     reply_markup=markups.settings)


@bot.message_handler(regexp='Язык')
def settings_language(message):
    msg = bot.send_message(message.chat.id, 'Выберите язык',
                           reply_markup=markups.choose_language)
    bot.register_next_step_handler(msg, settings_choose_language)


def settings_choose_language(message):
    if message.text == 'Назад':
        main_menu(message)
    else:
        if message.text in config.languages:
            requests.update_user_language(message.chat.id, message.text)
            bot.send_message(message.chat.id, 'Язык обновлен',
                             reply_markup=markups.settings)
        else:
            msg = bot.send_message(
                message.chat.id, 'Вы должны выбрать язык из списка', reply_markup=markups.choose_language)
            bot.register_next_step_handler(msg, settings_choose_language)


@bot.message_handler(regexp='Валюта')
def settings_fiat(message):
    msg = bot.send_message(message.chat.id, 'Выберите валюту',
                           reply_markup=markups.choose_fiat)
    bot.register_next_step_handler(msg, settings_choose_fiat)


def settings_choose_fiat(message):
    if message.text == 'Назад':
        main_menu(message)
    else:
        if message.text not in fiat_list():
            msg = bot.send_message(
                message.chat.id, 'Вы должны выбрать валюту из списка', reply_markup=markups.fiat_currencies)
            bot.register_next_step_handler(
                msg, settings_choose_fiat)
        else:
            requests.update_user_currency(message.chat.id, message.text)
            bot.send_message(message.chat.id, 'Валюта обновлена',
                             reply_markup=markups.settings)


def fiat_list():
    return [i['symbol'] for i in requests.get_currencies_list('fiat')]


if __name__ == "__main__":
    bot.polling()
