
import fastapi

import uvicorn


from api.db import init_db


from .routers import items, users, orders, currencies, categories, reviews


app = fastapi.FastAPI()
app.include_router(items.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(currencies.router)
app.include_router(categories.router)
app.include_router(reviews.router)


@app.on_event("startup")
def on_startup():
    init_db()




if __name__ == "__main__":
    uvicorn.run(app)


# FormData([('name', 'WAllet'), ('description', 'I found it'), ('currency', 'BTC_curr'), ('file', <starlette.datastructures.UploadFile object at 0x0000018171CD5940>), ('price', '111')])
