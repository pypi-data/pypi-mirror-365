# Corrected eio function (ONLY THE eval() LINE IS CHANGED)

import sys

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
        return True

    # Initialize eval_globals and eval_locals
    # It's better to explicitly initialize them to empty dicts before population
    eval_globals = {}
    eval_locals = {}

    if context is not None:
        # If context is explicitly provided, use it for evaluation
        eval_globals = context
        # When 'context' is the primary source, 'locals' can often be an empty dict
        # or the same as globals if you want all variables from context to be accessible as both
        # For simplicity with eval, passing the context as 'globals' is usually sufficient.
        # eval_locals = {} # You can explicitly set it if needed, or leave as default empty.
    else:
        # Attempt to get the context from the calling frame
        try:
            caller_frame = sys._getframe(1)
            eval_globals = caller_frame.f_globals
            eval_locals = caller_frame.f_locals
        except ValueError:
            # Fallback if _getframe doesn't work
            eval_globals = globals() # Global scope of the __init__.py file
            eval_locals = locals()   # Local scope of the eio function

    conditions_to_evaluate = conditions[0] if isinstance(conditions[0], list) else conditions

    for condition_str in conditions_to_evaluate:
        try:
            # THIS IS THE CRITICAL CHANGE: Pass eval_globals and eval_locals
            if not eval(condition_str, eval_globals, eval_locals):
                return False
        except Exception as e:
            if verbose:
                print(f"Error evaluating condition '{condition_str}': {e}")
            return False
    return True

__version__ = "0.1.3"