import fastapi
from fastapi import APIRouter
import fastapi
from sqlmodel import Session,  select
from api.db import get_session
from api.models import Category, CategoryBase


router = APIRouter(prefix="/categories",
                   tags=["categories"],
                   responses={404: {"description": "Not found"}})



@router.get('/get_list')
def get_list_categories(session: Session = fastapi.Depends(get_session)):
    with session:
        statement = select(Category)
        categories = session.exec(statement).fetchall()

        return categories



@router.post('/create')
def create_category(category: CategoryBase, session: Session = fastapi.Depends(get_session)):
    with session:
        category = Category(**category.dict())
        session.add(category)
        session.commit()
        session.refresh(category)

        return category

@router.get('/get_by_lang_item_type/{lang}/{item_type}')
def get_by_lang_item_type(lang: str, item_type: str, session: Session = fastapi.Depends(get_session)):
    """Returns list of categories by language and item type in format {'name': id}"""
    with session:
        statement = select(Category).where(Category.item_type == item_type)

        categories = session.exec(statement).fetchall()

        result = {}

        for category in categories:
            result[category.name[lang]] = category.id

        return result

@router.get('/get_by_lang_and_id/{lang}/{id}')
def get_category_by_lang_and_id(lang: str, id: int, session: Session = fastapi.Depends(get_session)):
    """Returns category by language and id in format {'name': id}"""
    with session:
        statement = select(Category).where(Category.id == id)

        category = session.exec(statement).one_or_none()

        if category is None:
            return None

        return category.name[lang]