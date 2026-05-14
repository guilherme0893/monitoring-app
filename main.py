from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.database import init_db

from routers.wells import wells


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(wells)
