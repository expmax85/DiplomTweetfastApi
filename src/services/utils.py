from fastapi.encoders import jsonable_encoder
from sqlalchemy import Row

from src.models import User


def key_gen(*args) -> str:
    return ":".join([str(arg) for arg in args])


def _to_json(data: dict) -> dict:
    for item in data["tweets"]:
        item["attachments"] = [i["image"] for i in item["attachments"]]
    return jsonable_encoder(data)


def serialize_user(user: User | Row) -> dict:
    return {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [usr.to_dict() for usr in user.followers],
            "following": [usr.to_dict() for usr in user.followed],
        },
    }
