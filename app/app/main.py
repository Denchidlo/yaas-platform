from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from sqladmin import Admin
import os
import logging


from app.api.v1.routes import api_router
from app.core.config import settings
from app.db.session import engine
from app.admin import *

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
admin = Admin(app, engine, authentication_backend=authentication_backend, title='YetAnotherAudioService')

admin.add_view(UserAdmin)
admin.add_view(RoleAdmin)
admin.add_view(EventAdmin)
admin.add_view(LogAdmin)
admin.add_view(AudioAdmin)