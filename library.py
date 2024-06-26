import datetime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Создание объекта FastAPI
app = FastAPI()

# Настройка базы данных MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://isp_p_Zasoba:12345@/77.91.86.135/isp_p_Zasoba"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Определение модели SQLAlchemy для пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)  # Указываем длину для VARCHAR
    email = Column(String(100), unique=True, index=True)  # Указываем длину для VARCHAR

class Readers(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True)
    reader_name = Column(String(50))
    surname = Column(String(50))
    patronymic = Column(String(50))
    address = Column(String(50))
    phone = Column(String(11))
    
    issuance = relationship("Issuance", back_populates="reader")

class Issuance(Base):
    __tablename__ = "issuance"

    id = Column(Integer, ForeignKey('reader.id'), primary_key=True, index=True)
    book_cipher = Column(String(30), ForeignKey('books.id'), primary_key=True, index=True)
    date_of_issue = Column(DateTime)
    signature = Column(String(50))
    
    reader = relationship("Readers", back_populates="issuance")
    book = relationship("Books", back_populates="issuance")

class Publishing(Base):
    __tablename__ = "publishing"

    id = Column(Integer, primary_key=True, index=True)
    publishing_name = Column(String(100))
    publishing_city = Column(String(50))
    
    books = relationship("Books", back_populates="publishing")

class Books(Base):
    __tablename__ = "books"

    book_cipher = Column(Integer, primary_key=True, index=True)
    book_name = Column(String(50))
    first_author = Column(String(50))
    year_of_publishing = Column(Integer)
    book_price_rub = Column(Integer)
    copies = Column(Integer)
    
    publishing_id = Column(Integer, ForeignKey('Publishing.publishing_id'))
    publishing = relationship("Publishing", back_populates="books")
    issuance = relationship("Issuance", back_populates="book")


# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Определение Pydantic модели для пользователя
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class BooksCreate(BaseModel):
    book_cipher: int
    book_name: str
    first_author: str
    year_of_publishing: int
    book_price_rub: int
    copies: int

class BooksResponse(BaseModel):
    id: int
    book_cipher: int
    book_name: str
    first_author: str
    year_of_publishing: int
    book_price_rub: int
    copies: int

  
class PublishingCreate(BaseModel):
    publishing_name: str
    publishing_city: str

class PublishingResponse(BaseModel):
    id: int
    publishing_name: str
    publishing_city: str

    
class IssuanceCreate(BaseModel):
    book_cipher: int
    date_of_issue: datetime.datetime
    signature: str

class IssuanceResponse(BaseModel):
    id: int
    book_cipher: int
    date_of_issue: str
    signature: str



class ReadersCreate(BaseModel):
    reader_name: str
    surname: str
    patronymic: str
    address: str
    phone: str


class ReadersResponse(BaseModel):
    id: int
    reader_name: str
    surname: str
    patronymic: str
    address: str
    phone: str

    class Config:
        orm_mode = True


# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршрут для получения пользователя по ID
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Маршрут для создания нового пользователя
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")


@app.get('/books/', response_model=BooksResponse)
def read_books(db: Session = Depends(get_db)):
    return db.query(Books).all()


@app.put('/books/{book_id}', response_model=BooksResponse)
def update_book(book_id: int, book: Books, db: Session = Depends(get_db)):
    db_books = db.query(Books).filter(Books.id == book_id).first()
    if db_books is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for var, value in vars(book).items():
        setattr(db_books, var, value) if value else None
    db.commit()
    db.refresh(db_books)
    return db_books


@app.post('/books/', response_model=BooksResponse)
def create_book(book: Books, db: Session = Depends(get_db)):
    db_book = Books(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_books)
    return db_books


@app.put("/publishing/{publishing_id}/", response_model=PublishingResponse)
def update_publishing(publishing_id: int, publishing: PublishingCreate, db: Session = Depends(get_db)):
    db_publishing = db.query(Publishing).filter(Publishing.id == publishing_id).first()
    if db_publishing is None:
        raise HTTPException(status_code=404, detail="Publishing not found")
    for var, value in vars(publishing).items():
        setattr(db_publishing, var, value) if value else None
    db.commit()
    db.refresh(db_publishing)
    return db_publishing


@app.get("/publishing/", response_model=PublishingResponse)
def get_publishers_with_books(db: Session = Depends(get_db)):
    publishing = db.query(Publishing).join(Books).distinct().all()
    return publishing

@app.post("/publishing/", response_model=PublishingResponse)
def create_publishing(publisher: PublishingCreate, db: Session = Depends(get_db)):
    db_publishing = Publishing(**publishing.dict())
    db.add(db_publishing)
    db.commit()
    db.refresh(db_publishing)
    return db_publishing

@app.get("/readers/{reader_id}", response_model=ReadersResponse)
def read_readers(reader_id: int, db: Session = Depends(get_db)):
    reader = db.query(Readers).filter(Readerse.reader_id == reader_id).first()
    if reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader

@app.get("/readers/overdue/", response_model=ReadersResponse)
def read_readers_with_overdue_books(db: Session = Depends(get_db)):
    overdue_books = db.query(Issuance).filter(Issuance.return_date < date.today()).all()
    readers = [issuance.reader for issuance in overdue_books]
    return readers

