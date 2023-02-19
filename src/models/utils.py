from fastapi.encoders import jsonable_encoder

from src.models import schemas


def to_json(data: schemas.TweetsSerialize) -> dict:
    result = jsonable_encoder(data)
    for item in result['tweets']:
        item['content'] = item.pop('tweet_data')
        item['attachments'] = [i['image'] for i in item['attachments']]
    return result
