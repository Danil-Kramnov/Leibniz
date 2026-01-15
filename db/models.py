from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class StatusEnum(enum.Enum):
    want_to_read = "want_to_read"
    reading = "reading"
    finished = "finished"


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String)
    file_id = Column(String, nullable=False, unique=True)
    file_unique_id = Column(String, unique=True)
    format = Column(String)
    page_count = Column(Integer)
    file_size = Column(Integer)
    category = Column(String)
    confidence = Column(Float)
    added_date = Column(DateTime, default=datetime.utcnow)


class ReadingStatus(Base):
    __tablename__ = 'reading_status'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    user_id = Column(Integer, nullable=False)
    status = Column(Enum(StatusEnum))
    started_date = Column(DateTime)
    finished_date = Column(DateTime)


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class BookTag(Base):
    __tablename__ = 'book_tags'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    tag_id = Column(Integer, ForeignKey('tags.id'))
