# This special import brings the generated code into the test's scope.
from temp_generated_code import fibonacci


def test_fibonacci_base_cases():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1


def test_fibonacci_positive_numbers():
    assert fibonacci(2) == 1
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55


def test_fibonacci_larger_number():
    assert fibonacci(15) == 610
