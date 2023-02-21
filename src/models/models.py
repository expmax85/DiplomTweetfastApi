from sqlalchemy import Column, Integer, String, ForeignKey, Table, ARRAY, Boolean
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
    tweet_media_ids = Column('tweet_media_ids', ARRAY(Integer), nullable=True)
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


class Follower(Base):
    __tablename__ = 'followers'

    follower_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    followed_id = Column(Integer, ForeignKey('users.id'), primary_key=True)


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
    hashed_password = Column('hashed_password', String(100), nullable=False)
    inactive = Column('inactive', Boolean, default=False)

    likes = relationship('Like', back_populates='user_likes', lazy=True)
    tweets = relationship('Tweet', back_populates='author')
    token = relationship('Token', back_populates='user')
    followers = relationship('Follower', primaryjoin="Follower.follower_id == User.id")
    followed = relationship('Follower', primaryjoin="Follower.followed_id == User.id")

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
