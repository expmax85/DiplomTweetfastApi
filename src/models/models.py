from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from src.database import engine
from src.database.database import SessionLocal

Base = declarative_base(bind=engine)


class Tweet(Base):
    """
    Relationship:
    O2O - Media
    M2O - User
    M2M - User(through Like)
    """
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    tweet_data = Column('tweet_data', String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='cascade'))

    author = relationship('User', back_populates='tweets')
    images = relationship('Media', back_populates='tweet')
    likes = relationship('Like', back_populates='tweet_likes', lazy=True)

    def is_author(self, user: 'User') -> bool:
        return self.user_id == user.id


class Media(Base):
    """
    Relationship:
    O2O - Tweet
    """
    __tablename__ = 'tweet_media'

    id = Column(Integer, primary_key=True)
    image = Column(String, default='some')
    tweet_media_ids = Column(ForeignKey('tweets.id', ondelete='cascade'))

    tweet = relationship('Tweet', back_populates='images')


followers = Table(
    'followers', Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id')),
    Column('followed_id', Integer, ForeignKey('users.id'))
)


class User(Base):
    """
    Relationship:
    O2O - Token
    O2M -User
    O2M - Tweet
    M2M - Tweet(through Like)
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False)

    likes = relationship('Like', back_populates='user_likes', lazy=True)
    tweets = relationship('Tweet', back_populates='author')
    token = relationship('Token', backref='user')
    followed = relationship('User', secondary=followers,
                            primaryjoin=(followers.c.follower_id == id),
                            secondaryjoin=(followers.c.followed_id == id),
                            backref=backref('followers', lazy='dynamic'),
                            lazy='dynamic')

    def follow(self, user: 'User') -> 'User':
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user: 'User') -> 'User':
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user: 'User') -> bool:
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def to_dict(self) -> dict:
        return {'id': self.id, 'name': self.name}


class Token(Base):
    """
    Relationship:
    O2O - User
    """
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id', ondelete='cascade'))
    api_key = Column(String(50), nullable=False)
    token_type = Column(String(50))


class Like(Base):
    __tablename__ = "likes"
    user_id = Column(ForeignKey("users.id"), primary_key=True)
    tweet_id = Column(ForeignKey("tweets.id"), primary_key=True)

    tweet_likes = relationship("Tweet", back_populates="likes")
    user_likes = relationship("User", back_populates="likes")


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
