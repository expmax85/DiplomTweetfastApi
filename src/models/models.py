from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.database import engine
from src.database.database import SessionLocal

Base = declarative_base(bind=engine)


class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    tweet_data = Column('tweet data', String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='tweets')
    images = relationship('Media', back_populates='tweet')
    likes = relationship('Like', back_populates='tweet')


class Media(Base):
    __tablename__ = 'tweet_media'

    id = Column(Integer, primary_key=True)
    image = Column(String, default='some')
    tweet_media_ids = Column(ForeignKey('tweets.id', ondelete='cascade'))

    tweet = relationship('Tweet', back_populates='images')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False)
    pid_user = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))

    follovers = relationship('User', remote_side=[id])
    likes = relationship('Like', back_populates='user')
    tweets = relationship('Tweet', back_populates='user')
    token = relationship('Token', backref='user')


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id', ondelete='cascade'))
    api_key = Column(String(50), nullable=False)


class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(ForeignKey('tweets.id', ondelete='cascade'))
    user_id = Column(ForeignKey('users.id', ondelete='cascade'))

    tweet = relationship('Tweet', back_populates='likes')
    user = relationship('User', back_populates='likes')


def init_db():
    Base.metadata.create_all(bind=engine)


def create_users():
    session = SessionLocal()
    if not session.query(User).all():
        users = [
            User(name='John'),
            User(name='Mike'),
            User(name='Lily')
        ]
        users[0].token.append(Token(api_key='test'))
        users[1].token.append(Token(api_key='mike_secret_token'))
        users[2].token.append(Token(api_key='lily_secret_token'))
        session.add_all(users)
        session.commit()
        session.close()
