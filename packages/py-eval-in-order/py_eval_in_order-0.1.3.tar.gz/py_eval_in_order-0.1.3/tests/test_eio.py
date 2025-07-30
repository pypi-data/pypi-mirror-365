# tests/test_eio.py
import pytest
import sys
from py_eio_logic import eio # Import your eio function

# --- Test Cases for Basic Functionality ---

def test_eio_basic_true_single_condition():
    assert eio("1 == 1") is True

def test_eio_basic_true_multiple_conditions():
    assert eio("1 < 2", "True and True") is True

def test_eio_basic_false_single_condition():
    assert eio("1 != 1") is False

def test_eio_basic_false_multiple_conditions_short_circuit():
    # The second condition should not be evaluated
    assert eio("1 > 2", "2 + 2 == 5") is False

def test_eio_empty_conditions():
    assert eio() is True

def test_eio_list_input():
    conditions_list = ["10 > 5", "5 == 5", "True"]
    assert eio(conditions_list) is True

def test_eio_list_input_false():
    conditions_list = ["10 > 5", "5 != 5", "True"]
    assert eio(conditions_list) is False

# --- Test Cases for 'context' Parameter (Explicit Variable Passing) ---

def test_eio_with_explicit_context_true():
    my_vars = {'x': 10, 'y': 5}
    assert eio("x > 8", "y == 5", context=my_vars) is True

def test_eio_with_explicit_context_false():
    my_vars = {'a': 100, 'b': 20}
    assert eio("a < 50", "b > 10", context=my_vars) is False # short-circuits on a < 50

def test_eio_with_explicit_context_missing_variable_verbose_true(capsys):
    my_vars = {'val': 10}
    result = eio("val > 5", "missing_var < 10", context=my_vars, verbose=True)
    assert result is False
    captured = capsys.readouterr()
    assert "Error evaluating condition 'missing_var < 10': name 'missing_var' is not defined" in captured.out

def test_eio_with_explicit_context_missing_variable_verbose_false(capsys):
    my_vars = {'val': 10}
    result = eio("val > 5", "missing_var < 10", context=my_vars, verbose=False)
    assert result is False
    captured = capsys.readouterr()
    # No error message should be printed when verbose=False
    assert "Error evaluating condition 'missing_var < 10'" not in captured.out

def test_eio_with_explicit_context_short_circuit_missing_variable(capsys):
    # This tests that the NameError is NOT raised if short-circuited, regardless of verbose
    my_vars = {'val': 10}
    result = eio("1 == 2", "missing_var < 10", context=my_vars, verbose=True) # verbose=True, but short-circuited
    assert result is False
    captured = capsys.readouterr()
    assert "Error evaluating condition 'missing_var < 10'" not in captured.out


# --- Test Cases for Inferred Context (using sys._getframe) ---

# Define variables in the local scope of the test functions for inferred context
def test_eio_with_inferred_context_true():
    # Variables _x and _y are local to this test function
    _x = 15
    _y = 25
    assert eio("_x + _y == 40") is True

def test_eio_with_inferred_context_false():
    _val1 = 5
    _val2 = 10
    assert eio("_val1 > 10", "_val2 == 10") is False # short-circuits on _val1 > 10

def test_eio_with_inferred_context_missing_variable_verbose_true(capsys):
    # 'non_existent_var' is not defined in this scope
    result = eio("True", "non_existent_var > 0", verbose=True)
    assert result is False
    captured = capsys.readouterr()
    assert "Error evaluating condition 'non_existent_var > 0': name 'non_existent_var' is not defined" in captured.out

def test_eio_with_inferred_context_missing_variable_verbose_false(capsys):
    # 'non_existent_var' is not defined in this scope
    result = eio("True", "non_existent_var > 0", verbose=False)
    assert result is False
    captured = capsys.readouterr()
    assert "Error evaluating condition 'non_existent_var > 0'" not in captured.out

def test_eio_with_inferred_context_short_circuit_missing_variable(capsys):
    # This should short-circuit before evaluating 'non_existent_var_2'
    result = eio("1 == 0", "non_existent_var_2 > 0", verbose=True) # verbose=True, but short-circuited
    assert result is False
    captured = capsys.readouterr()
    assert "Error evaluating condition 'non_existent_var_2 > 0'" not in captured.out

# --- Test Cases for Other Exceptions ---

def test_eio_syntax_error_in_condition_verbose_true(capsys):
    result = eio("if True: pass", verbose=True) # Invalid syntax for eval()
    assert result is False
    captured = capsys.readouterr()
    assert "Error evaluating condition 'if True: pass':" in captured.out
    assert "SyntaxError" in captured.out

def test_eio_syntax_error_in_condition_verbose_false(capsys):
    result = eio("if True: pass", verbose=False)
    assert result is False
    captured = capsys.readouterr()
    assert "Error evaluating condition 'if True: pass'" not in captured.out

def test_eio_type_error_in_condition_verbose_true(capsys):
    my_data = {'text': "hello"}
    result = eio("text + 1", context=my_data, verbose=True)
    assert result is False
    captured = capsys.readouterr()
    assert "Error evaluating condition 'text + 1':" in captured.out
    assert "TypeError" in captured.out

def test_eio_type_error_in_condition_verbose_false(capsys):
    my_data = {'text': "hello"}
    result = eio("text + 1", context=my_data, verbose=False)
    assert result is False
    captured = capsys.readouterr()
    assert "Error evaluating condition 'text + 1'" not in captured.out