from sqlalchemy import create_engine  # create_engine 用来创建与数据库的连接，只有有了连接后才能操作数据库
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#SQLALCHEMY_DATABASE_URL = 'sqlite:///./todoapp.db' # sqlite3  数据库路径为当前目录下的名为 todoapp.db 的文件
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:200492@localhost:5432/todoapplication' # postgresql

""" 
创建数据库连接。
"check_same_thread": False, 允许多个线程共享数据库连接(sqlite 默认要求在同一个线程内访问数据库)
"""
#engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  # sqlite3
engine = create_engine(SQLALCHEMY_DATABASE_URL)

""" 
创建数据库会话对象。
sessionmaker() 是一个工厂函数, 用来创建数据库会话对象。
SessionLocal 是一个会话类, 用于每次数据库操作时创建一个会话实例。
    autocommit=False 表示在会话中, commit 操作需要显式地调用, 而不是自动提交。
    autoflush=False 表示会话不会自动刷新（刷新指的是将数据推送到数据库）。
    bind=engine 表示会话将与创建的 engine(数据库连接)相绑定。
"""
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""  
声明基础模型类。
declarative_base() 是一个工厂函数, 用来创建基类 Base。
所有的数据库模型类都需要继承这个 Base 类。
"""
Base = declarative_base()

def get_db():
    db = SessionLocal()  # 创建数据库会话，用来查询和操作数据库
    try:
        yield db # 这是一个生成器，将数据库会话提供给调用者
    finally:
        db.close() # 当数据库会话完成后，关闭会话