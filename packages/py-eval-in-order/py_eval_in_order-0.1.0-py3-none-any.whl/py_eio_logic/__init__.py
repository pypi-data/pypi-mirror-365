# py_eio_logic/__init__.py

def eio(*conditions):
    """
    Evaluates multiple string conditions, returning True if all are met.

    WARNING: This function uses eval() and should ONLY be used with trusted
    input strings to prevent severe security vulnerabilities.
    Untrusted input can lead to arbitrary code execution.

    Args:
        *conditions: One or more string expressions to evaluate.
                     If the first argument is a list, it iterates over that list.
                     Otherwise, it iterates over the positional arguments.

    Returns:
        bool: True if all conditions evaluate to True, False otherwise.
    """
    if not conditions:
        # If no conditions are provided, it's vacuously true
        return True

    # Check if the first argument is a list; if so, iterate over its elements.
    # Otherwise, iterate over the conditions tuple directly.
    conditions_to_evaluate = conditions[0] if isinstance(conditions[0], list) else conditions

    for condition_str in conditions_to_evaluate:
        # CRITICAL SECURITY NOTE: eval() is dangerous with untrusted input.
        # Ensure 'condition_str' comes from a trusted, controlled source.
        try:
            if not eval(condition_str):
                return False
        except Exception as e:
            # Handle potential errors during evaluation (e.g., invalid syntax, NameError)
            print(f"Error evaluating condition '{condition_str}': {e}")
            return None
    return True

__version__ = "0.1.0"

# Optional: You can make the function directly accessible via 'from py_eio_logic import eio'
# by putting it here, or just let users access it via 'import py_eio_logic; py_eio_logic.eio()'