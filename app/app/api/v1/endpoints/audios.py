from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.models.audio import Audio

router = APIRouter()


@router.get("/", response_model=List[schemas.Audio])
async def read_audios(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 9,
) -> Any:
    """
    Retrieve audios.
    """
    return await crud.audio.get_multi(db, skip=skip, limit=limit)


@router.get("/by-filename/{key}", response_model=schemas.Audio)
async def read_audio_by_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    key: str,
    check_liked: int = 0
) -> Any:
    """
    Retrieve active audio for active user by key.
    """
    audio = await crud.audio.get_by_key(
        db=db, key=key
    )
    return audio


@router.post("/", response_model=schemas.Audio)
async def create_audio(
    *,
    db: AsyncSession = Depends(deps.get_db),
    audio_in: schemas.AudioCreate
) -> Any:
    """
    Create new audio.
    """
    audio = await crud.audio.create(db=db, obj_in=audio_in)
    return audio


@router.get("/{id}", response_model=schemas.Audio)
async def read_audio(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int
) -> Any:
    """
    Get audio by ID.
    """
    audio = await crud.audio.get(db=db, id=id)
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return audio


@router.delete("/{id}", response_model=schemas.Audio)
async def delete_audio(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a audio.
    """
    audio = await crud.audio.get(db=db, id=id)
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    audio = await crud.audio.remove(db=db, id=id)
    return audio
