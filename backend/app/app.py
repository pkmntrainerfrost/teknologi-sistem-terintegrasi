from beanie import init_beanie
from fastapi import Depends, FastAPI

from app.db.db import db_database
from app.schemas.schemas import UserCreate, UserRead, UserUpdate
from app.auth.user import auth_backend, current_active_user, fastapi_users
from app.models.models import User, CommissionSlot, Commission,Df,TfIdf

from app.routes.commissionslots import router as commissionslots_routes
from app.routes.commissions import router as commissions_routes

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    commissionslots_routes, prefix="/commissionslots"
)
app.include_router(
    commissions_routes, prefix="/commissions"
)


@app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=db_database,
        document_models=[
            User,CommissionSlot,Commission,Df,TfIdf
        ],
    )
