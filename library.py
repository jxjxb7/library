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
    reader_name = Column(String(50), index=True)
    surname = Column(String(50), index=True)
    patronymic = Column(String(50), index=True)
    address = Column(String(50), index=True)
    phone = Column(String(11), index=True)

class Issuance(Base):
    __tablename__ = "issuance"

    id = Column(Integer, primary_key=True, index=True)
    book_cipher = Column(String(30), index=True)
    date_of_issue = Column(String(50), index=True)
    signature = Column(String(50), index=True)

class Publishing(Base):
    __tablename__ = "publishing"

    id = Column(Integer, primary_key=True, index=True)
    publishing_name = Column(String(100), index=True)
    publishing_city = Column(String(50), index=True)

class Books(Base):
    __tablename__ = "books"

    book_cipher = Column(Integer, primary_key=True, index=True)
    book_name = Column(String(50), index=True)
    first_author = Column(String(50), index=True)
    year_of_publishing = Column(Integer, index=True)
    book_price_rub = Column(Integer, index=True)
    copies = Column(Integer, index=True)


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

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True


class PublishingCreate(BaseModel):
    publishing_name: str
    publishing_city: str

class PublishingResponse(BaseModel):
    id: int
    publishing_name: str
    publishing_city: str

    class Config:
        orm_mode = True

class IssuanceCreate(BaseModel):
    book_cipher: int
    date_of_issue = str
    signature = str

class IssuanceResponse(BaseModel):
    id: int
    book_cipher: int
    date_of_issue = str
    signature = str

    class Config:
        orm_mode = True

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
