import fastapi
from fastapi import APIRouter
import fastapi
from sqlmodel import Session, select
from sqlalchemy import func
from api.db import get_session
from api.models import (Review, ReviewBase)


router = APIRouter(prefix="/reviews",
                   tags=["reviews"],
                   responses={404: {"description": "Not found"}})

@router.get('/get_by_order/{item_id}')
async def get_reviews_for_order(item_id: int, session: Session = fastapi.Depends(get_session)):
    """Return list of reviews for order by order_id"""
    with session:
        statement = select(Review).where(Review.item_id == item_id)
        result = session.exec(statement)
        return result.fetchall()

@router.get('/get_by_user/{user_id}')
async def get_reviews_for_user(user_id: int, session: Session = fastapi.Depends(get_session)):
    """Return list of reviews about user by user_id"""
    with session:
        statement = select(Review).where(Review.seller_id == user_id)
        result = session.exec(statement)
        return result.fetchall()

@router.get('/get_count/{user_id}')
async def get_count_reviews_by_user_id(user_id: int, session: Session = fastapi.Depends(get_session)):
    """Return count of positive and negative reviews for user by user_id"""
    with session:
        statement = select(func.count(Review.id)).where(Review.seller_id == user_id, Review.rating >= 4)
        positive = session.exec(statement)

        statement = select(func.count(Review.id)).where(Review.seller_id == user_id, Review.rating < 4)
        negative = session.exec(statement)

        result = {'positive': positive.one_or_none(), 'negative': negative.one_or_none()}
        return result

@router.post('/create')
async def create_review(review: ReviewBase, session: Session = fastapi.Depends(get_session)):
    """Create new review"""
    with session:
        review = Review(**review.dict())

        session.add(review)
        session.commit()
        session.refresh(review)
        return review

