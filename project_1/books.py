from fastapi import Body, FastAPI  # get 只能读，所以没有 body

app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'},
]

# Get all books
@app.get("/books")
async def read_all_books():
    return BOOKS

# Get a book by title
@app.get("/books/bytitle/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():  # casefold()，统一将字符串转换为小写。毕竟是一个方法，后面的括号不能丢，否则会报错
            return book
        
# Get books by author
@app.get("/books/byauthor/{author}")
async def read_books_by_author(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get("author").casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return

# Get books by category
@app.get("/books/bycategory/{category}")
async def read_books_by_category(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get("category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

# Get books by author and category
@app.get("/books/{book_author}/")
async def read_books_by_category(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
            book.get('category').casefold() == category.casefold():
                books_to_return.append(book)
    return books_to_return

# Create a new book
@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)

# Update an existing book
@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == updated_book.get("title").casefold():
            BOOKS[i] = updated_book
            break

# Delete a book
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break
