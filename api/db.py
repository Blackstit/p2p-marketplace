
from sqlmodel import create_engine, SQLModel, Session
import os

DBUSERNAME = os.environ.get('DBUSERNAME')
DBPASSWORD = os.environ.get('DBPASSWORD')

engine = create_engine("mysql://{DBUSERNAME}:{DBPASSWORD}@localhost/superapp?charset=utf8mb4".format(DBUSERNAME=DBUSERNAME, DBPASSWORD=DBPASSWORD), echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

init_db()