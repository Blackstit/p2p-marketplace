from telebot.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
import api.requests as requests
import itertools


back_button = KeyboardButton('Назад')


main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Маркет', 'Настройки')

market = ReplyKeyboardMarkup(resize_keyboard=True)
market.add('Товары', 'Услуги', 'Задания', 'Селлеры', 'Профиль')
market.add('Главное меню')


back = ReplyKeyboardMarkup(resize_keyboard=True)
back.add(back_button)


profile = ReplyKeyboardMarkup(resize_keyboard=True)
profile.add('Мои товары', 'Мои услуги', 'Мои задания',
            'Пополнить баланс', 'Вывести деньги', 'Мои сделки', 'Мои отзывы')
profile.add(back_button)


settings = ReplyKeyboardMarkup(resize_keyboard=True)
settings.add('Язык', 'Валюта', 'Рефералка', 'Наш чат',
             'Наш канал', 'Написать в поддержку')
settings.add(back_button)

cryptocurrencies_list = requests.get_currencies_list('crypto')
cryptocurrencies = ReplyKeyboardMarkup(resize_keyboard=True)
print(cryptocurrencies_list)
cryptocurrencies.add(*[i['symbol'] for i in cryptocurrencies_list])

fiat_currencies_list = requests.get_currencies_list('fiat')
fiat_currencies = ReplyKeyboardMarkup(resize_keyboard=True)
fiat_currencies.add(*[i['symbol'] for i in fiat_currencies_list])


deposit = InlineKeyboardMarkup()
deposit.add(*[InlineKeyboardButton(i['symbol'], callback_data='deposit_{}'.format(i['symbol']))
            for i in cryptocurrencies_list])


my_orders = ReplyKeyboardMarkup(resize_keyboard=True)
my_orders.add('История сделок', 'Активные сделки')
my_orders.add(back_button)


choose_language = ReplyKeyboardMarkup(resize_keyboard=True)
choose_language.add('RU', 'EN')
choose_language.add(back_button)


choose_fiat = ReplyKeyboardMarkup(resize_keyboard=True)
choose_fiat.add(*[i['symbol'] for i in fiat_currencies_list])
choose_fiat.add(back_button)

empty_markup = ReplyKeyboardMarkup(resize_keyboard=True)
