import fastapi
from fastapi import APIRouter
import fastapi
from sqlmodel import Session, select, and_
from api.db import get_session
from api.models import OrderBase, Orders


router = APIRouter(prefix="/orders",
                   tags=["orders"],
                   responses={404: {"description": "Not found"}})



@router.get('/get_order/{id}')
async def get_order(id: int, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Orders).where(Orders.id == id)
        order = session.exec(statement).one_or_none()

        return order


@router.get('/get_by_user_list/{user_id}')
async def get_orders_by_user_id(user_id: int, session: Session = fastapi.Depends(get_session)):
    """Returns list of orders where user id equals to buyer id"""
    with session:
        statement = select(Orders).where(Orders.buyer == user_id)
        orders = session.exec(statement).fetchall()

        return orders


@router.get('/get_active_by_user_list/{user_id}')
async def get_orders_by_user_id(user_id: int, session: Session = fastapi.Depends(get_session)):
    """Returns list of orders where user id equals to buyer id"""
    with session:
        statement = select(Orders).where(
            and_(Orders.buyer == user_id, Orders.status == 'In process'))
        orders = session.exec(statement).fetchall()

        return orders


@router.put('/update_order_status/')
async def update_order_status(id: int, status: str,  session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Orders).where(Orders.id == id)
        order = session.exec(statement).one_or_none()
        if order is not None:
            order.status = status
            session.add(order)
            session.commit()
            session.refresh(order)

            return order


@router.post('/create_order')
async def create_order(order: OrderBase, session: Session = fastapi.Depends(get_session)):
    """Order is created when buyer clicks on 'Buy' button."""
    with session:
        order = Orders(**order.dict())

        session.add(order)
        session.commit()
        session.refresh(order)

        return order

@router.put('/set_application_message_id/')
async def set_application_message_id(id: int, seller_message_id: int, buyer_message_id: int, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Orders).where(Orders.id == id)
        order = session.exec(statement).one_or_none()
        if order is not None:
            order.seller_application_message_id = seller_message_id
            order.buyer_application_message_id = buyer_message_id
            session.add(order)
            session.commit()
            session.refresh(order)

            return order