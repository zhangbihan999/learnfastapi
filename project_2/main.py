from fastapi import Body, FastAPI, Path, Query, HTTPException
from book import *
from book_request import *
from starlette import status  # 定制化状态码返回内容

app = FastAPI()

BOOKS = [
    Book(1, "Computer Science Pro", "codingwithzc", "Nice book", 5, 2030),
    Book(2, "Be Fast with FastAPI", "codingwithzc", "Nice book", 5, 2030),
    Book(3, "Master Endpoints", "codingwithzc", "Nice book", 5, 2029),
    Book(4, "HP1", "Author 1", "Book Description", 2, 2028),
    Book(5, "HP2", "Author 2", "Book Description", 3, 2027),
    Book(6, "HP3", "Author 3", "Book Description", 1, 2026),
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found.")
        
@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_books_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_books_by_published_date(published_date: int = Query(gt=1999, lt=2031)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

# 将新添加书籍的 id 修改为合理的值
def find_book_id(book: Book):
    book.id = (BOOKS[-1].id + 1) if len(BOOKS) > 0 else 1
    return book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i] = book_request
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found.")

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found.")