"""
Custom exceptions
"""

from colorama import Back, Fore, Style, init

init(strip=False)


class ExamException(Exception):
    """
    Base exception for custom exception
    """


class TestFuncNameError(ExamException):
    """
    Error for when test function name is wrong
    """


class TestClassNameError(ExamException):
    """
    Error for when test class name is wrong
    """


class MissingDir(ExamException):
    """
    Error for when src dir is missing and can't change working dir.
    """

    DEFAULT_MSG = (
        Style.BRIGHT + Back.BLACK + Fore.RED + "\n*********\n"
        "Katalogen som ska innehålla din kod saknas.\n"
        "Kontrollera att du har katalogen {missing_path}.\n"
        "Om du har den och felet kvarstår, kontakta kursansvarig med ovanstående felmeddelande!"
        "\n*********" + Style.RESET_ALL
    )

    def __init__(self, missing_path):
        self.message = self.DEFAULT_MSG.format(missing_path=missing_path)
        super().__init__(self.message)


class ContactError(ExamException):
    """
    Custom error. Used when there is an error in the test code and the
    student should contact the person responsible for the exam.
    """

    DEFAULT_MSG = (
        Style.BRIGHT + Back.BLACK + Fore.RED + "\n*********\n"
        "Något gick fel i rättningsprogrammet. "
        "Kontakta Ansvarig med ovanstående felmeddelande!"
        "\n*********" + Style.RESET_ALL
    )

    def __init__(self, message=DEFAULT_MSG):
        self.message = message
        super().__init__(self.message)
