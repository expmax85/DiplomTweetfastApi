from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref, DeclarativeBase, Mapped, mapped_column

from src.database import engine
from src.database.database import SessionLocal


class Base(DeclarativeBase):
    pass


class Tweet(Base):
    """
    Relationship:
    O2O - Media
    M2O - User
    M2M - User(through Like)
    """
    __tablename__ = 'tweets'

    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_data: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates='tweets')
    attachments: Mapped[list["Media"]] = relationship(back_populates='tweet')
    likes: Mapped[list["Like"]] = relationship(back_populates='tweet')

    def is_author(self, user: 'User') -> bool:
        return self.user_id == user.id


class Media(Base):
    """
    Relationship:
    O2O - Tweet
    """
    __tablename__ = 'tweet_media'

    id: Mapped[int] = mapped_column(primary_key=True)
    image: Mapped[str] = mapped_column(String(20))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    tweet: Mapped["Tweet"] = relationship(back_populates='attachments')


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

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

    likes: Mapped[list["Like"]] = relationship(back_populates='user_likes', lazy=True)
    tweets: Mapped[list["Tweet"]] = relationship(back_populates='author')
    token: Mapped["Token"] = relationship(backref='user')
    followed: Mapped[list["User"]] = relationship(secondary=followers,
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

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    api_key: Mapped[str] = mapped_column(String(50))


class Like(Base):
    __tablename__ = "likes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), primary_key=True)

    tweet: Mapped[list["Tweet"]] = relationship(back_populates="likes")
    user_likes: Mapped[list["User"]] = relationship(back_populates="likes")


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
        users[0].token = Token(api_key='test')
        users[1].token = Token(api_key='mike_secret_token')
        users[2].token = Token(api_key='lily_secret_token')
        session.add_all(users)
        session.commit()
        session.close()
