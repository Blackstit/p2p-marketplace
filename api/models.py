from datetime import datetime
from email.mime import application

from typing import Union, Dict
from unicodedata import category
from sqlalchemy import table
from sqlmodel import JSON, Column, SQLModel, Field


class ItemsBase(SQLModel):
    """creator_id is the id of the user who created the item
        name is the name of the item
        description is the description of the item
        price is the price of the item
        image is the file_id of image of the item
        category is the category of the item
        type is either product or service or task
    """
    creator_id: int 
    name: str = ''
    description: str = ''
    category: str = ''
    currency: str  = None
    price: float = 0
    rating: float = 0
    votes: int = 0
    images: str  = None
    type: str  = None



class CurrencyBase(SQLModel):
    """Name: name of the currency used for coingecko api (for fiat it's the same with lowercase symbol)
    Symbol: symbol of the currency
    type: fiat or crypto
    address: address of the currency (if crypto)
    decimals: number of decimals
    """
    name: str
    symbol: str
    type: str
    address: str
    decimals: int

class UserBase(SQLModel):
    name: str
    rating: float = 0
    votes: int = 0
    language: str  = None
    currency: str  = None
    balance: Union[Dict[str, float], None] = Field(sa_column=Column(JSON))

    class Config:
        arbitrary_types_allowed = True


class OrderBase(SQLModel):
    buyer: int
    seller: int
    ad_type: str
    ad_id: int
    price: float
    currency: str
    seller_application_message_id: Union[int, None] = None
    buyer_application_message_id: Union[int, None] = None ###used to edit the message when buyer cancels order
    status: str = 'application sent'
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)

class CategoryBase(SQLModel):
    """name is dict of name of the category in different languages"""
    item_type: str = 'product'
    name: dict = Field(sa_column=Column(JSON))


class ReviewBase(SQLModel):
    """review_id is the id of the review
        item_id is the id of the item
        user_id is the id of the user who wrote the review
        seller_id is the id of the user who sold the item
        rating is the rating of the review
        text is the text of the review
    """
    item_id: int
    user_id: int
    seller_id: int
    rating: float
    text: str
    


class Item(ItemsBase, table=True):
    id: int = Field(default=None, primary_key=True)
    is_popular: bool = False

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    is_popular: bool = False

class Currencies(CurrencyBase, table=True):
    id: int = Field(default=None, primary_key=True)

class Orders(OrderBase, table=True):
    id: int = Field(default=None, primary_key=True)

class Category(CategoryBase, table=True):
    id: int = Field(default=None, primary_key=True)

class Review(ReviewBase, table=True):
    id: int = Field(default=None, primary_key=True)