from typing import TypeVar, Generic
from math import ceil
from pydantic import BaseModel

T = TypeVar("T")


def paginate(items: list[T], page: int, per_page: int, total: int) -> dict:
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": ceil(total / per_page) if per_page > 0 else 0
    }
