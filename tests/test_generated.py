import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sample_module

def test_hello_baseline():
    """Baseline auto-generated test for hello."""
    try:
        result = sample_module.hello("")
        assert result is not None or result == 0 or result == '' or result == []
    except Exception as e:
        pytest.fail(f'Function hello raised {type(e).__name__}: {e}')

def test_add_baseline():
    """Baseline auto-generated test for add."""
    try:
        result = sample_module.add(0, 0)
        assert result is not None or result == 0 or result == '' or result == []
    except Exception as e:
        pytest.fail(f'Function add raised {type(e).__name__}: {e}')


# =============================
# LLM-Generated Enhanced Tests
# =============================

# Tests for hello
import pytest
import sample_module

def test_hello_valid_input():
    """Test hello with a valid name."""
    name = "Alice"
    result = sample_module.hello(name)
    assert result == f"Hello, {name}!", f"Expected personalized greeting for valid name '{name}'"

def test_hello_empty_input():
    """Test hello with an empty string as input."""
    name = ""
    result = sample_module.hello(name)
    assert result == "Hello, !", "Expected 'Hello, !' for empty input"

def test_hello_none_input():
    """Test hello with None as input.  Should return 'Hello, World!'."""
    name = None
    result = sample_module.hello(name)
    assert result == "Hello, World!", "Expected 'Hello, World!' for None input"

def test_hello_numeric_input():
    """Test hello with a numeric value as input. Should treat it as a string."""
    name = 123
    result = sample_module.hello(name)
    assert result == "Hello, 123!", "Expected personalized greeting with number treated as string"

def test_hello_special_characters():
    """Test hello with a name containing special characters."""
    name = "!@#$%^"
    result = sample_module.hello(name)
    assert result == "Hello, !@#$%^!", "Expected personalized greeting with special characters"

def test_hello_long_name():
    """Test hello with a very long name."""
    name = "ThisIsAVeryLongNameThatExceedsReasonableLimits"
    result = sample_module.hello(name)
    assert result == f"Hello, {name}!", "Expected personalized greeting for long name"

# Tests for add
import pytest
import sample_module
from typing import Any


def test_add_valid_integers():
    """Test add with valid positive integer inputs."""
    result = sample_module.add(5, 3)
    assert result == 8, "add(5, 3) should return 8"


def test_add_strings():
    """Test add with string inputs.  Should perform concatenation."""
    result = sample_module.add("hello", "world")
    assert result == "helloworld", "add('hello', 'world') should return 'helloworld'"


def test_add_mixed_types_integer_first():
    """Test add with mixed types (int and str) - str concatenation TypeError."""
    with pytest.raises(TypeError) as excinfo:
        sample_module.add(5, "world")
    assert "can only concatenate str (not \"int\") to str" in str(excinfo.value)

