from datetime import datetime
from typing import Literal

from graphiti_core_falkordb.utils.datetime_utils import utc_now
from pydantic import BaseModel, Field


class Result(BaseModel):
    message: str
    success: bool


class Message(BaseModel):
    content: str = Field(..., description='The content of the message')
    uuid: str | None = Field(default=None, description='The uuid of the message (optional)')
    name: str = Field(
        default='', description='The name of the episodic node for the message (optional)'
    )
    role_type: Literal['user', 'assistant', 'system'] = Field(
        ..., description='The role type of the message (user, assistant or system)'
    )
    role: str | None = Field(
        description='The custom role of the message to be used alongside role_type (user name, bot name, etc.)',
    )
    timestamp: datetime = Field(default_factory=utc_now, description='The timestamp of the message')
    source_description: str = Field(
        default='', description='The description of the source of the message'
    )
    source_url: str | None = Field(
        default=None, description='The URL or file path of the source document/file'
    )
    source_metadata: dict | None = Field(
        default=None, description='Additional metadata about the source (file size, type, etc.)'
    )
