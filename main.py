from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.database import init_db
from seed import seed

from routers.wells import wells
from routers.readings import readings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(wells)
app.include_router(readings)
