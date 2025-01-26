from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base
import pytest
from models import Todos, Users
from routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'zc', 'id': 1, 'role': 'admin'}

@pytest.fixture
def test_todo():
    todo = Todos(
        title='learn to code',
        description='need to do everyday',
        priority=5,
        complete=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield db  # 将 db 提供给需要它的测试函数，从而使测试函数可以对 db 进行操作

    # yield 能够将测试工作的执行与前后所需的工作分开

    # 测试函数执行完成后，自动执行 yield 后面也就是下面这段代码来清理数据库环境
    with engine.connect() as connection: # 建立数据库连接
        connection.execute(text("delete from todos;"))  # 执行删除操作
        connection.commit()  # 使数据库修改生效

@pytest.fixture
def test_user():
    user = Users(
        email='example@email.com',
        username='zc',
        first_name='bihan',
        last_name='zhang',
        hashed_password=bcrypt_context.hash("testpassword"),
        is_active=True,
        role='admin',
        phone_number='12345678901'
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    with engine.connect() as connection:
        connection.execute(text("delete from users;"))
        connection.commit()