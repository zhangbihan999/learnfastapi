import pytest

def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1

def test_is_instance():
    assert isinstance('hello', str)
    assert not isinstance('10', int)

class Student():
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years

@pytest.fixture    # 创建一个可重用的实例
def default_employee():
    return Student('chen', 'zhang', 'Software Engineer', 3)

def test_person_initialization(default_employee):
    assert default_employee.first_name == 'chen'
    assert default_employee.last_name == 'zhang'
    assert default_employee.major == 'Software Engineer'
    assert default_employee.years == 3