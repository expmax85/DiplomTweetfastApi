from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


class Tweet(Base):
    """
    Relationship:
    O2O - Media
    M2O - User
    M2M - User(through Like)
    """
    __tablename__ = 'tweets'

    id = Column('id', Integer, primary_key=True)
    tweet_data = Column('content', String(100), nullable=False)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='cascade'))

    author = relationship('User', back_populates='tweets')
    attachments = relationship('Media', back_populates='tweet')
    likes = relationship('Like', back_populates='tweet')

    def is_author(self, user: 'User') -> bool:
        return self.user_id == user.id


class Media(Base):
    """
    Relationship:
    O2O - Tweet
    """
    __tablename__ = 'tweet_media'

    id = Column('id', Integer, primary_key=True)
    image = Column('image', String, default='some')
    tweet_id = Column('tweet_id', ForeignKey('tweets.id', ondelete='cascade'))

    tweet = relationship('Tweet', back_populates='attachments')


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

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(15), nullable=False)

    likes = relationship('Like', back_populates='user_likes', lazy=True)
    tweets = relationship('Tweet', back_populates='author')
    token = relationship('Token', back_populates='user')
    followed = relationship('User', secondary=followers,
                            primaryjoin=(followers.c.follower_id == id),
                            secondaryjoin=(followers.c.followed_id == id),
                            backref=backref('followers'))

    def follow(self, user: 'User') -> 'User':
        self.followed.append(user)
        return self

    def unfollow(self, user: 'User') -> 'User':
        self.followed.remove(user)
        return self

    def to_dict(self) -> dict:
        return {'id': self.id, 'name': self.name}

    def __repr__(self) -> str:
        return str(self.name)

    # def __eq__(self, other) -> bool:
    #     if not isinstance(other, User):
    #         return False
    #     return other.id == self.id


class Token(Base):
    """
    Relationship:
    O2O - User
    """
    __tablename__ = 'tokens'

    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='cascade'))
    api_key = Column('api_key', String(50), nullable=False)

    user = relationship('User', back_populates='token', lazy="joined")


class Like(Base):
    __tablename__ = "likes"
    user_id = Column('user_id', ForeignKey("users.id", ondelete='cascade'), primary_key=True)
    tweet_id = Column('tweet_id', ForeignKey("tweets.id", ondelete='cascade'), primary_key=True)

    tweet = relationship("Tweet", back_populates="likes")
    user_likes = relationship("User", back_populates="likes")
