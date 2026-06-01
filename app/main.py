from fastapi import FastAPI

from api.routers import provider_router

app = FastAPI(title="Notification Service (Technical Test)")

app.include_router(provider_router.router)
