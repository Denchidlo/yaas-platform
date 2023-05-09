from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.models.log import Log

router = APIRouter()


@router.get("/", response_model=List[schemas.Log])
async def read_logs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 9,
) -> List[Log]:
    """
    Retrieve recognition logs.
    """
    return await crud.log.get_multi(db, skip=skip, limit=limit)


@router.get("/search", response_model=List[schemas.Log])
async def read_recognition_logs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 9,
) -> List[Log]:
    """
    Retrieve audios.
    """
    return await crud.audio.get_multi_by_type(db, skip=skip, limit=limit, type="RecognitionRequest")


@router.get("/hosting", response_model=List[schemas.Log])
async def read_hosting_logs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 9,
) -> List[Log]:
    """
    Retrieve search logs.
    """
    return await crud.log.get_multi_by_type(db, skip=skip, limit=limit, type="HostingRequest")
