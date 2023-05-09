from sqladmin import ModelView
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import User, Role, Log, Event, Audio
from app.core.security import get_password_hash


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
        User.email,
        User.created_at,
        User.updated_at,
        User.active,
        User.role_id,
    ]
    
    async def on_model_change(self, data: dict, model: User, is_created: bool):
        data['hashed_password'] = get_password_hash(data['hashed_password'])
        return await super().on_model_change(data, model, is_created)


class RoleAdmin(ModelView, model=Role):
    column_list = [
        Role.id,
        Role.role_name,
    ]


class EventAdmin(ModelView, model=Event):
    column_list = [
        Event.id,
        Event.event_name,
    ]


class LogAdmin(ModelView, model=Log):
    column_list = [
        Log.id,
        Log.event_dt,
        Log.event_id,
        Log.log_payload,
    ]

class AudioAdmin(ModelView, model=Audio):
    column_list = [
        Audio.id,
        Audio.filename,
        Audio.file_sha1,
        Audio.dt_created,
        Audio.dt_modified,
        Audio.fingerprinted,
        Audio.total_hashes,
    ]
