from sqlalchemy import ARRAY, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

__all__ = ("Base", "Tweet", "Like", "User", "Media", "Token", "Follower")


class Base(DeclarativeBase):
    ...


class Tweet(Base):
    """
    Relationship:
    O2O - Media
    M2O - User
    M2M - User(through Like)
    """

    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tweet_data: Mapped[str] = mapped_column("content", String(100), nullable=False)
    tweet_media_ids: Mapped[list[int]] = mapped_column(
        "tweet_media_ids", ARRAY(Integer), nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        "user_id", ForeignKey("users.id", ondelete="cascade")
    )

    author: Mapped["User"] = relationship(
        "User", back_populates="tweets", uselist=False
    )
    attachments: Mapped[list["Media"]] = relationship("Media", back_populates="tweet")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="tweet")

    def is_author(self, user: "User") -> bool:
        return self.user_id == user.id


class Media(Base):
    """
    Relationship:
    O2O - Tweet
    """

    __tablename__ = "tweet_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image: Mapped[str] = mapped_column("image", String(100))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id", ondelete="cascade"))

    tweet: Mapped["Tweet"] = relationship(
        "Tweet", back_populates="attachments", uselist=False
    )


class Follower(Base):
    __tablename__ = "followers"

    follower_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )
    followed_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )


class User(Base):
    """
    Relationship:
    O2O - Token
    O2M -User
    O2M - Tweet
    M2M - Tweet(through Like)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(15), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    inactive: Mapped[bool] = mapped_column(Boolean, default=False)

    likes: Mapped[list["Like"]] = relationship(
        "Like", back_populates="user_likes", lazy=True
    )
    tweets: Mapped[list["Tweet"]] = relationship("Tweet", back_populates="author")
    token: Mapped["Token"] = relationship("Token", back_populates="user", uselist=False)
    followed: Mapped[list["User"]] = relationship(
        "User",
        secondary="followers",
        primaryjoin="User.id == Follower.follower_id",
        secondaryjoin="User.id == Follower.followed_id",
        backref="followers",
    )

    def follow(self, user: "User") -> "User":
        self.followed.append(user)
        return self

    def unfollow(self, user: "User") -> "User":
        self.followed.remove(user)
        return self

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}

    def __repr__(self) -> str:
        return str(self.name)

    def __eq__(self, item: object) -> bool:
        if not isinstance(item, User):
            raise TypeError("object is not instance User")
        return self.id == item.id


class Token(Base):
    """
    Relationship:
    O2O - User
    """

    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"))
    api_key: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="token", lazy="joined", uselist=False
    )


class Like(Base):
    __tablename__ = "likes"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), primary_key=True
    )
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweets.id", ondelete="cascade"), primary_key=True
    )

    tweet: Mapped["Tweet"] = relationship(
        "Tweet", back_populates="likes", uselist=False
    )
    user_likes: Mapped["User"] = relationship(
        "User", back_populates="likes", uselist=False
    )
