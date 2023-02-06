from src.database import engine, UserAction
from src.database.database import SQLSession
from src.models import User, Token

async_session = SQLSession()


async def create_users():
    async with async_session as db:
        # user_orm = UserAction(db=db)
        # users = await user_orm.get_all()
        # if len(users) < 1:
        users = [
            User(name='John'),
            User(name='Mike'),
            User(name='Lily')
        ]
        users[0].token.append(Token(api_key='test'))
        users[1].token.append(Token(api_key='mike_secret_token'))
        users[2].token.append(Token(api_key='lily_secret_token'))
        db.session.add_all(users)
