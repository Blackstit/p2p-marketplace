import fastapi
from fastapi import APIRouter
import fastapi
from sqlmodel import Session,  select
from api.db import get_session
from api.models import Currencies, CurrencyBase


router = APIRouter(prefix="/currencies",
                   tags=["currencies"],
                   responses={404: {"description": "Not found"}})



@router.get('/get_list/{type}')
def get_list_currencies(type: str, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Currencies).where(Currencies.type == type)
        currencies = session.exec(statement).fetchall()

        return currencies


@router.get('/get_symbols')
def get_list_currencies_symbols(session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Currencies.symbol)
        currencies = session.exec(statement).fetchall()

        return currencies


@router.get('/get_by_symbol/{symbol}')
def get_list_currency_by_symbol(symbol: str, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Currencies).where(Currencies.symbol == symbol)
        currencies = session.exec(statement).one_or_none()

        return currencies


@router.post('/create')
def create_currency(currency: CurrencyBase, session: Session = fastapi.Depends(get_session)):
    with session:
        currency = Currencies(**currency.dict())
        session.add(currency)
        session.commit()
        session.refresh(currency)

        return currency