from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401


async def init_db(db: AsyncSession) -> None:
    admin_role = await crud.role.get_by_name(db, 'Admin')
    user_role = await crud.role.get_by_name(db, 'User')
    if not admin_role:
        admin_role = await crud.role.create(db, obj_in={'role_name': 'Admin'})  # noqa: F841
    if not user_role:
        admin_role = await crud.role.create(db, obj_in={'role_name': 'User'})  # noqa: F841

    user = await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    test_user = await crud.user.get_by_email(db, email='test@test.com')
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            role_id=admin_role.id,
        )
        user = await crud.user.create(db, obj_in=user_in)  # noqa: F841
    if not test_user:
        test_user_in = schemas.UserCreate(
            email='test@test.com',
            password='test',
            role_id=user_role.id,
        )
        test_user = await crud.user.create(db, obj_in=test_user_in)  # noqa: F841  