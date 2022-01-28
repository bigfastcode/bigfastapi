from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

class Book(BaseModel):
    book_name: str
    author_name: str
    genre: Optional[str] = None
    publish_year: Optional[int] = None

app = FastAPI()

@app.post("/books/")
def create_book(book: Book):
    return book



@app.post("/books/")
def create_book(book: Book):
    book_dict = book.dict()
    description = book.book_name + "/**" + book.author_name + "/**" + str(book.publish_year)
    book_dict.update({"description": description})
    return book_dict

@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    return {"book_id": book_id, **book.dict()}