import fastapi
from fastapi import APIRouter
import fastapi
from sqlmodel import Session, or_, select, and_
from api.db import get_session
from api.models import (Item, ItemsBase, User)


router = APIRouter(prefix="/items",
                   tags=["items"],
                   responses={404: {"description": "Not found"}})


@router.get('/get_list/{item_type}')
async def get_list_items(item_type: str = None, session: Session = fastapi.Depends(get_session)):
    with session:
        if item_type is None:
            statement = select(Item)
        else:
            statement = select(Item).where(Item.type == item_type)
        result = session.exec(statement)
        return result.fetchall()


@router.get('/get_list_popular/{item_type}')
async def get_list_items(item_type: str, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Item).where(
            and_(Item.is_popular == True, Item.type == item_type))
        result = session.exec(statement)
        return result.fetchall()


@router.get('/search/{item_type}/{search}')
async def get_item(item_type: str, search: str, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Item).where(and_(
            or_(Item.name.contains(search),  Item.description.contains(search)), Item.type == item_type))
        result = session.exec(statement)
        return result.fetchall()


@router.get('/get_by_user/{item_type}/{user_id}')
async def search_item(item_type: str, user_id: int, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Item).where(
            and_(Item.creator_id == user_id), Item.type == item_type)
        result = session.exec(statement)
        return result.fetchall()


@router.get('/{id}')
async def get_item(id: int, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Item).where(Item.id == id)
        result = session.exec(statement)
        return result.one_or_none()


@router.post('/create')
async def create_item(item: ItemsBase, session: Session = fastapi.Depends(get_session)):
    item = Item(**item.dict())
    print(item.json())
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@router.put('/update')
async def update_item(id: int, name: str = None, price: float = None, images: str = None, description: str = None,  session: Session = fastapi.Depends(get_session)):
    with session:
        try:
            statement = select(Item).where(Item.id == id)
            result = session.exec(statement)

            item_new = result.one_or_none()

            if name is not None:
                item_new.name = name
            if price is not None:
                item_new.price = price
            if images is not None:
                item_new.images = images
            if description is not None:
                item_new.description = description

            session.add(item_new)
            session.commit()
            session.refresh(item_new)

            return item_new
        except:
            return fastapi.Response(status_code=503)


@router.put('/vote')
async def vote_for_item(id: int, rating: int, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Item).where(Item.id == id)
        result = session.exec(statement)

        item = result.one_or_none()
        item.rating = round(
            (item.rating*item.votes + rating) / (item.votes + 1), 2)
        item.votes += 1

        statement = select(User).where(User.id == item.creator_id)
        result = session.exec(statement)

        user = result.one_or_none()
        user.rating = round(
            (user.rating*user.votes + rating) / (user.votes + 1), 2)
        user.votes += 1

        session.add(item)
        session.commit()
        session.refresh(item)

        session.add(user)
        session.commit()
        session.refresh(user)

        statement = select(Item).where(Item.id == id)
        item = session.exec(statement).one_or_none()

        return item


@router.delete('/delete/')
async def delete_item(id: int, session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Item).where(Item.id == id)

        item = session.exec(statement).one_or_none()
        if item is not None:
            session.delete(item)
            session.commit()

        return {}
