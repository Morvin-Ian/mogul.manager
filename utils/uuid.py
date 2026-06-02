import uuid as _uuid


def is_valid_uuid(v: str) -> bool:
    try:
        _uuid.UUID(v)
        return True
    except ValueError:
        return False
