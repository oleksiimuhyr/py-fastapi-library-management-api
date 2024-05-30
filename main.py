from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import schemas
import crud
from database import SessionLocal

app = FastAPI()


@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'All works correct at this endpoint'}


def get_db() -> Session:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get('/authors/', response_model=list[schemas.Author])
def read_all_authors(
        db: Session = Depends(get_db),
        limit: int | None = None,
        skip: int | None = None,
) -> list[schemas.Author]:
    return crud.get_list_of_authors(db=db, skip=skip, limit=limit)


@app.post('/authors/', response_model=schemas.Author)
def create_author(
        author: schemas.AuthorCreate,
        db: Session = Depends(get_db)
) -> schemas.Author:
    db_authors = crud.get_author_by_name(db=db, name=author.name)

    if db_authors:
        raise HTTPException(
            status_code=400, detail='This Author already exist')
    return crud.create_author(db=db, author=author)


@app.get('/authors/{author_id}/', response_model=schemas.Author)
def read_author_by_id(author_id: int,
                      db: Session = Depends(get_db)) -> schemas.Author:
    db_author = crud.get_author_by_id(db=db, author_id=author_id)

    if db_author is None:
        raise HTTPException(status_code=404, detail='Author not found')

    return db_author


@app.post('/books/', response_model=schemas.Book)
def create_book(
        book: schemas.BookCreate,
        db: Session = Depends(get_db)
) -> schemas:
    db_book = crud.get_book_by_title(db=db, title=book.title)

    if db_book:
        raise HTTPException(status_code=400,
                            detail='Book with this name already exist')
    return crud.create_book(db=db, book=book)


@app.get('/books/', response_model=List[schemas.Book])
def read_all_books(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[schemas.Book]:
    return crud.get_list_of_books(db=db, skip=skip, limit=limit)


@app.get('/books/author/{author_id}/', response_model=list[schemas.Book])
def read_books_by_author(author_id: int,
                         db: Session = Depends(get_db)) -> List[schemas.Book]:
    books = crud.get_book_by_author_id(db=db, author_id=author_id)
    if not books:
        raise HTTPException(status_code=404,
                            detail='No books found for this author')
    return books
