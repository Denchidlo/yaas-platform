from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models import Role
from app.schemas.role import RoleCreate, RoleUpdate

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_name(self, db: AsyncSession, name: str) -> Role:
        result = await db.execute(select(Role).where(Role.role_name == name))
        return result.scalars().first()

role = CRUDRole(Role)