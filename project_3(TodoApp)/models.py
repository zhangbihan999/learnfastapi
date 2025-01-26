from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean 

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)

class Todos(Base):  # 继承自 Base，所以是一个 ORM 模型类，会映射至数据库中的某张表(下面指定的 todos 表)
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True) # index=True 表示会为该列创建索引，以加速基于该字段的查询
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))