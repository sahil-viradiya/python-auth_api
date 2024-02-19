import asyncio

from fastapi import FastAPI



from database import init_model, engine
from routers import user

app = FastAPI()

if __name__ == "__main__":
    asyncio.run(init_model(engine))

app.router.include_router(user.router)
