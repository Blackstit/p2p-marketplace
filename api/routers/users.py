import api.exchange
import fastapi
from fastapi import APIRouter
from fastapi import Response
from sqlmodel import Session, and_, select
from sqlalchemy import func
from api.db import get_session
from api.models import Currencies, User, Orders
from typing import Dict

router = APIRouter(prefix="/users",
                   tags=["users"],
                   responses={404: {"description": "Not found"}})



@router.post('/create_user')
async def create_user(user: User, session: Session = fastapi.Depends(get_session)):
    with session:
        print('user has added')
        session.add(user)
        session.commit()
        session.refresh(user)

        return user


@router.get('/get_user/{id}')
async def get_user(id: int, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(User).where(User.id == id)

        user = session.exec(statement).one_or_none()

        return user


@router.put('/update_balance')
async def update_balance(user_id: int, balance: Dict[str, float], session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).one_or_none()

        if user is not None:
            if user.balance is None:
                user.balance = {}

            for currency in balance:
                user.balance[currency] = balance[currency]

            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(user, 'balance')

            session.add(user)
            session.commit()
            session.refresh(user)

            return user
        else:
            return Response(content='User does not exists', status_code=404)


@router.put('users/update_language')
async def update_user_language(user_id: int, language: str, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).one_or_none()

        if user is not None:
            user.language = language

            session.add(user)
            session.commit()
            session.refresh(user)

            return user
        else:
            return Response(content='User does not exists', status_code=404)


@router.put('users/update_currency')
async def update_user_currency(user_id: int, currency: str, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).one_or_none()

        if user is not None:
            user.currency = currency

            session.add(user)
            session.commit()
            session.refresh(user)

            return user
        else:
            return Response(content='User does not exists', status_code=404)


@router.get('/get_orders_volume/{user_id}')
async def get_orders_volume(user_id: int, session: Session = fastapi.Depends(get_session)):
    """Returns volume of user's deals in format {{'spent': int, 'received': int}}"""
    with session:
        currencies_statement = select(Currencies).where(Currencies.type == 'crypto')

        currencies = session.exec(currencies_statement).fetchall()

        user_statement = select(User).where(User.id == user_id)
        user = session.exec(user_statement).one_or_none()

        received, spent = 0, 0

        for currency in currencies:
            statement_received = select(func.sum(Orders.price)).where(and_(Orders.seller == user_id, Orders.currency == currency.symbol))
            statement_spent = select(func.sum(Orders.price)).where(and_(Orders.buyer == user_id, Orders.currency == currency.symbol))


            exchange = api.exchange.get_price(currency.name, user.currency.lower())

            print(exchange, 'exchange')

            received_sum = session.exec(statement_received).one_or_none() 
            
            spent_sum = session.exec(statement_spent).one_or_none()

            received += received_sum * exchange if received_sum is not None else 0
            spent += spent_sum * exchange if spent_sum is not None else 0

        return {'received': received, 'spent': spent}

            

@router.get('/get_popular_sellers')
async def get_popular_sellers(session: Session = fastapi.Depends(get_session)):
    """Returns list of popular sellers"""
    with session:
        statement = select([User]).where(User.is_popular == True)
        result = session.exec(statement)

        return result.fetchall()

@router.get('/count_deals/{user_id}')
async def get_count_of_deals_by_user_id(user_id: int, session: Session = fastapi.Depends(get_session)):
    """Returns count of seller's deals"""
    with session:
        statement = select(func.count(Orders.id)).where(Orders.seller == user_id)
        result = session.exec(statement)

        return result.one_or_none()