"""
Sample test files for coding agent testing
"""

SAMPLE_PYTHON_HELLO = '''
def hello():
    """Simple hello function"""
    print("Hello!")

if __name__ == "__main__":
    hello()
'''

SAMPLE_PYTHON_MATH = '''
def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract two numbers"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b
'''

SAMPLE_PYTHON_WITH_TESTS = '''
import pytest

def test_add():
    from math_utils import add
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    from math_utils import subtract
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
'''

SAMPLE_PYTHON_BAD_SYNTAX = '''
def broken_function(
    print("Missing closing parenthesis"
    return None

def another_bad():
    if True
        print("Missing colon")
'''

SAMPLE_PYTHON_STYLE_ISSUES = '''
def badStyleFunction( x,y ):
    if x>y:
        return x
    else:
        return y

def another_function():
    unused_var = 10
    return 5
'''
