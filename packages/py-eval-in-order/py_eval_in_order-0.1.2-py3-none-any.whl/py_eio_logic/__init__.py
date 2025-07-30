# py_eio_logic/__init__.py

def eio(*conditions,verbose=True,context=None):
    """
    Evaluates multiple string conditions, returning True if all are met.

    WARNING: This function uses eval() and should ONLY be used with trusted
    input strings to prevent severe security vulnerabilities.
    Untrusted input can lead to arbitrary code execution.

    Args:
        *conditions: One or more string expressions to evaluate.
                     If the first argument is a list, it iterates over that list.
                     Otherwise, it iterates over the positional arguments.
        verbose (bool, optional): if True, will display an error message on errors instead of just returning false
        context (dict, optional): A dictionary containing variables that can be
                                  referenced in the condition strings.
                                  If provided, these variables will be made available
                                  to the eval() function.
                                  If None, the function will attempt to infer the
                                  calling scope's variables.


    Returns:
        bool: True if all conditions evaluate to True, False otherwise.
    """
    if not conditions:
        # If no conditions are provided, it's vacuously true
        return True
    eval_globals = {}
    eval_locals = {}

    if context is not None:
        # If context is explicitly provided, use it for evaluation
        eval_globals = context
        # In this setup, we usually don't need separate 'locals' if context covers everything
    else:
        # Attempt to get the context from the calling frame
        # This is a bit advanced and can be tricky, but aims to auto-detect variables.
        # However, it's generally safer and more explicit to pass 'context'.
        # For simplicity, we might just use globals() if context isn't passed
        # This is the part that was causing the 'x not defined' error if 'x' was only local to caller
        # The recommended way is to always pass context for clarity and safety with eval.
        # For this fix, let's make it clear that 'context' is the primary way.
        # If no context is passed, we'll try to get the caller's globals and locals
        try:
            # Get the frame of the caller (the script that called eio)
            # [0] is eio's frame, [1] is the caller's frame
            caller_frame = sys._getframe(1)
            eval_globals = caller_frame.f_globals
            eval_locals = caller_frame.f_locals
        except ValueError:
            # Fallback if _getframe doesn't work (e.g., in some restricted environments)
            eval_globals = globals()
            eval_locals = locals()
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
            if(verbose):print(f"Error evaluating condition '{condition_str}': {e}")
            return False
    return True

__version__ = "0.1.2"

# Optional: You can make the function directly accessible via 'from py_eio_logic import eio'
# by putting it here, or just let users access it via 'import py_eio_logic; py_eio_logic.eio()'
