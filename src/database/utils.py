from src.models import User, Token
from src.models.utils import get_password_hash
from . import SQLSession, UserAction

async_session = SQLSession()


async def create_users():
    async with async_session as db:
        user_orm = UserAction(db=db)
        users = await user_orm.get_all()
        if len(users) < 1:
            users = [
                User(name='John', hashed_password=get_password_hash('123456')),
                User(name='Mike', hashed_password=get_password_hash('234567')),
                User(name='Lily', hashed_password=get_password_hash('345678'))
            ]
            users[0].token.append(Token(api_key='test'))
            users[1].token.append(Token(api_key='mike_token'))
            users[2].token.append(Token(api_key='lily_token'))
            db.session.add_all(users)
