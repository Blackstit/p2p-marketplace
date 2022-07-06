from io import StringIO
from api.models import Item, User
import api.requests as requests
import api.exchange as exchange
import telebot
import telebot.types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import strings
from bot.main import reviews_count
import csv

languages = {'RU': 'rus', 'EN': 'eng'}


def show_item(item_id: int, bot: telebot.TeleBot, message, show_edit: bool = False, id: int = 0):
    item = Item(**requests.get_product(item_id))

    item_type = {'product': 'Товар', 'service': 'Услуга', 'task': 'Задание'}

    seller = User(**requests.get_user(item.creator_id))

    text = strings.item_text

    text = text.format(product=item,
                       item_type=item_type[item.type],
                       seller_name=bot.get_chat(seller.id).first_name,
                       seller=seller,
                       seller_reviews=reviews_count(seller.id),
                       seller_deals=requests.get_count_of_deals_by_user_id(
                           seller.id)
                       )

    markup = InlineKeyboardMarkup()
    if not show_edit:
        markup.add(InlineKeyboardButton(
            'Купить', callback_data='buy_{}'.format(item_id)))
    else:
        markup.add(InlineKeyboardButton('Редактировать',
                                        callback_data='edit_item{}'.format(item_id)))

    if item.images is not None:
        bot.send_photo(message.chat.id, item.images,
                    caption=text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.delete_message(message.chat.id, message.message_id)


def list_items(bot, message, request_function, text, c_data, id=0, sort_key: str = None,  **kwargs):
    items = request_function(**kwargs)

    markup = InlineKeyboardMarkup()
    if len(items) > 0:
        print(c_data)
        if 'seller' not in c_data:
            markup.add(InlineKeyboardButton('Фильтр по цене', callback_data=c_data +
                       '_' + items[0]['type'] + '_' + str(id) + '_price'))

        if sort_key is not None:
            if 'category' not in str(sort_key):
                items = sorted(items, key=lambda x: x[sort_key])
            else:
                user = requests.get_user(message.chat.id)
                category = requests.get_category_by_lang_and_id(
                    lang=user['language'], id=items[0]['category'])
                print('CATEGORY\n\n\n', category, sort_key,
                      user['language'], items[0]['category'])
                items = [item for item in items if category == sort_key.split('_')[
                    1]]

    if len(items) > 5:
        pages = len(items) // 5 + 1

        items = list(split(items, pages))

        for item in items[id]:

            item_data = get_item_data(c_data, item)
            markup.add(InlineKeyboardButton(
                text=item['name'], callback_data=item_data))

        if id > 0:
            markup.add(InlineKeyboardButton(
                'Назад', callback_data='{c_data}_{id}'.format(c_data=c_data, id=id-1)))
        if id < len(items) - 1:
            markup.add(InlineKeyboardButton(
                'Вперед', callback_data='{c_data}_{id}'.format(c_data=c_data, id=id+1)))

    else:
        for item in items:

            print('item is', item)
            if c_data != 'seller':
                item_data = get_item_data(c_data, item)
            else:
                item_data = 'show_seller{}'.format(item['id'])
            markup.add(InlineKeyboardButton(
                text=item['name'], callback_data=item_data))
    if len(items) > 0:
        if 'seller' not in c_data and 'mylist' not in c_data:
            markup.add(InlineKeyboardButton(
                'Поиск по имени', callback_data='search_{item_type}'.format(item_type=items[0]['type'])))
            markup.add(InlineKeyboardButton(
                'Выбор категории', callback_data='category_{item_type}'.format(item_type=items[0]['type'])))

        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Ничего не найдено')


def get_item_data(c_data, item):
    item_data = 'my' * (c_data == 'mylist') + 'show_{}'.format(item['id'])
    return item_data


def submit_edit(message, item_id, bot: telebot.TeleBot, c: telebot.types.CallbackQuery, **kwargs):
    item = Item(**requests.get_product(item_id))
    item.update(**kwargs)
    item.save()
    bot.send_message(message.chat.id, 'Изменения сохранены')


def get_full_balance(user_id):
    currencies = requests.get_currencies_list('crypto')
    user = requests.get_user(user_id)

    balance = 0

    if user['balance'] is not None:
        for currency in currencies:
            if currency['symbol'] in user['balance']:
                balance += exchange.get_price(
                    currency['name'], user['currency'].lower()) * user['balance'][currency['symbol']]

    text = 'Баланс кошелька: ≈<b>{} {}</b>'.format(balance, user['currency'])

    return text


def split(l, n):
    """Splits list into n chunks"""
    k, m = divmod(len(l), n)
    return (l[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def get_csv(l: list):
    """Return csv from list of dicts"""
    keys = l[0].keys()

    if 'seller' in keys:
        keys.remove('seller')

    return ','.join(keys) + '\n' + '\n'.join(','.join(str(v) for v in d.values()) for d in l)
