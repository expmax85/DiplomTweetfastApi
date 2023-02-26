from src.database import SQLSession, cruds

tweet_orm = cruds.TweetAction(db=SQLSession())
