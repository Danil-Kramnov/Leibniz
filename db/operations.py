from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from db.models import Base, Book, ReadingStatus, StatusEnum
from config import DATABASE_URL
from datetime import datetime

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def save_book(title, author, file_id, file_unique_id, format, page_count, file_size, category, confidence):
    session = Session()
    book = Book(
        title=title,
        author=author,
        file_id=file_id,
        file_unique_id=file_unique_id,
        format=format,
        page_count=page_count,
        file_size=file_size,
        category=category,
        confidence=confidence
    )
    session.add(book)
    session.commit()
    book_id = book.id
    session.close()
    return book_id


def search_books(query):
    session = Session()
    books = session.query(Book).filter(
        or_(
            Book.title.ilike(f'%{query}%'),
            Book.author.ilike(f'%{query}%')
        )
    ).limit(10).all()
    session.close()
    return books


def get_book(book_id):
    session = Session()
    book = session.query(Book).filter(Book.id == book_id).first()
    session.close()
    return book


def get_books_by_category(category):
    session = Session()
    books = session.query(Book).filter(Book.category == category).all()
    session.close()
    return books


def get_random_book():
    session = Session()
    book = session.query(Book).order_by(func.random()).first()
    session.close()
    return book


def get_reading_queue(user_id):
    session = Session()
    books = session.query(Book).join(ReadingStatus).filter(
        ReadingStatus.user_id == user_id,
        ReadingStatus.status == StatusEnum.want_to_read
    ).all()
    session.close()
    return books


def get_currently_reading(user_id):
    session = Session()
    books = session.query(Book).join(ReadingStatus).filter(
        ReadingStatus.user_id == user_id,
        ReadingStatus.status == StatusEnum.reading
    ).all()
    session.close()
    return books


def update_status(book_id, user_id, status):
    session = Session()
    rs = session.query(ReadingStatus).filter(
        ReadingStatus.book_id == book_id,
        ReadingStatus.user_id == user_id
    ).first()

    if rs:
        rs.status = status
        if status == StatusEnum.reading:
            rs.started_date = datetime.utcnow()
        elif status == StatusEnum.finished:
            rs.finished_date = datetime.utcnow()
    else:
        rs = ReadingStatus(
            book_id=book_id,
            user_id=user_id,
            status=status,
            started_date=datetime.utcnow() if status == StatusEnum.reading else None,
            finished_date=datetime.utcnow() if status == StatusEnum.finished else None
        )
        session.add(rs)

    session.commit()
    session.close()


def update_book_category(book_id, category):
    session = Session()
    book = session.query(Book).filter(Book.id == book_id).first()
    if book:
        book.category = category
        session.commit()
    session.close()


def get_stats(user_id):
    session = Session()
    total = session.query(Book).count()
    reading = session.query(ReadingStatus).filter(
        ReadingStatus.user_id == user_id,
        ReadingStatus.status == StatusEnum.reading
    ).count()
    finished = session.query(ReadingStatus).filter(
        ReadingStatus.user_id == user_id,
        ReadingStatus.status == StatusEnum.finished
    ).count()
    queue = session.query(ReadingStatus).filter(
        ReadingStatus.user_id == user_id,
        ReadingStatus.status == StatusEnum.want_to_read
    ).count()
    session.close()
    return total, reading, finished, queue


def book_exists(file_unique_id):
    session = Session()
    exists = session.query(Book).filter(Book.file_unique_id == file_unique_id).first() is not None
    session.close()
    return exists
