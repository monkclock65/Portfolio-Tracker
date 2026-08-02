import uuid
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class GUID(TypeDecorator):
    impl = PG_UUID(as_uuid=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(str(value))   # string -> real UUID
        return value