
import math

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 5 - 3 == 2

def test_string_upper():
    assert "hello".upper() == "HELLO"

def test_list_length():
    sample = [1,2,3,4]
    assert len(sample) == 4

def test_square_root():
    assert math.isclose(math.sqrt(16), 4.0)
