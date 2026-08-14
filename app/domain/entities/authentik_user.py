from uuid import UUID

from pydantic import BaseModel


class AuthentikUser(BaseModel):
    username: str
    pk: int
    uuid: UUID

