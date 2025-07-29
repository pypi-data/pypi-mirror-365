"""
Create a method for each type of common error.
Use common_errors to connect the method to an exception type.
"""

from .cli_parser import parse
from .helper_functions import COLORS


def check_if_common_error(exc_name, tb_exc, _):
    """
    Call all methods connected to an exception type.
    Return str from method if returned.
    Para _ should be "msg" if we find a use for it. Is "_" to pass validation
    """
    common_errors = {
        "StopIteration": [
            wrong_nr_of_input_calls,
        ],
        "AssertionError": [
            assertion_traceback,
        ],
        "SystemExit": [
            using_exit,
        ],
    }
    try:
        methods = common_errors[exc_name]
    except KeyError:
        return ""
    for method in methods:
        res = method(tb_exc)
        if res:
            return COLORS["BL"] + COLORS["BR"] + res + COLORS["RE"]
    return ""


def wrong_nr_of_input_calls(tb_exc):
    """
    Check if the exception match where the student make to many input() calls.
    """
    help_msg = (
        "(Tips! Det är vanligt att få detta felet om man gör fler "
        "anrop till funktionen input() än vad det står i uppgiften.)"
    )
    tb_str = "\n".join(list(tb_exc.format()))
    if "input(" in tb_str:
        if "mock_call" in tb_str:
            if "result = next(effect)" in tb_str:
                return help_msg
    return ""


def using_exit(tb_exc):
    """
    Catch errors if the student has used exit() or sys.exit()
    """
    help_msg = (
        "(Tips! Ditt program har använt exit() eller sys.exit() för att avsluta programmet. "
        "Det ska bara användas för att avsluta programmet när ett fel inträffar. "
        "Det borde inte användas för värdena som används i detta test.)"
        "\nOm det står i instruktionerna att du ska använda exit() eller sys.exit() "
        "för dessa värden, "
        "så är det ett fel i instruktionerna. Kontakta läraren för att få hjälp."
    )
    tb_str = "\n".join(list(tb_exc.format()))
    if "exit(" in tb_str or "sys.exit(" in tb_str:
        return help_msg
    return ""


def assertion_traceback(tb_exc):
    """
    Catch errors if --trace flag is set
    """
    ARGS = parse()

    if ARGS.trace_assertion_error:
        traceback = "\n".join(list(tb_exc.format()))

        return COLORS["M"] + "\n" + traceback + COLORS["RE"]
    return ""
