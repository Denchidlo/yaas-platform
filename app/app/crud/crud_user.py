from typing import Any, Dict, Optional, Union, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, and_

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> User:
        result = await db.execute(
            select(self.model)
                .where(self.model.id == id)
                .options(joinedload(User.role))
            )
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(
            select(User)
            .where(
                and_(User.email == email, User.active == True)
            ).options(joinedload(User.role)))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            connected_account_id=obj_in.connected_account_id if obj_in.connected_account_id else obj_in.email.split('@')[0],
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def get_extended_user(self, db: AsyncSession, id: Any) -> User:
        result = await db.execute(
            select(User)
            .where(and_(User.id == id))
            .options(joinedload(User.role))
        )
        return result.scalars().first()

    def is_active(self, user: User) -> bool:
        return user.active

    def is_superuser(self, user: User) -> bool:
        return user.role.role_name == 'Admin'


user = CRUDUser(User)