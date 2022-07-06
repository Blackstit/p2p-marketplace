item_text = """
{item_type} {product.name}
Продавец: {seller_name}
Рейтинг: {seller.rating} {seller_reviews}
Провел сделок: {seller_deals}

Описание:
{product.description}

Цена: {product.price} {product.currency}
"""


item_types = {'Товары': 'product',
              'товар': 'product',
              'услуга': 'service',
              'услугу': 'service',
              'товара': 'product',
              'услуги': 'service',
              'задания': 'task',
              'задание': 'task',
              'Услуги': 'service',
              'Задания': 'task'}

item_type_genitive = {'product': 'товара',
                      'service': 'услуги',
                      'task': 'задания'}

item_type_genitive_plural = {'product': 'товаров',
                             'service': 'услуг',
                             'task': 'заданий'}

item_type_nominative = {'product': 'Товар',
                        'service': 'Услуга',
                        'task': 'Задание'}
