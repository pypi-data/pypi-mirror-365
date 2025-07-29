"""
pass
"""

import hashlib
import importlib.util as importer
import os
import re
import sys
from functools import wraps
from pathlib import Path
from unittest import SkipTest

from colorama import Fore, Style, init

from .exceptions import MissingDir

init(strip=False)


COLOR_REGEX_START = r"\|(\w)\|"
COLOR_REGEX_STOP = r"\|/(\w)\|"
COLORS = {
    "G": Fore.GREEN,
    "B": Fore.BLACK,
    "R": Fore.RED,
    "Y": Fore.YELLOW,
    "BL": Fore.BLUE,
    "M": Fore.MAGENTA,
    "C": Fore.CYAN,
    "W": Fore.WHITE,
    "RE": Fore.RESET,
    "BR": Style.BRIGHT,
}


def list_to_hash(error):
    """
    hash a list
    """
    hash_obj = hashlib.sha1(bytes("".join(error), "utf-8"))
    return hash_obj.hexdigest()


def clean_str(string):
    """
    Remove cluther form students answer string.
    """
    return string.replace(chr(27) + "[2J" + chr(27) + "[;H", "")


def error_is_missing_assignment_function(error):
    """
    Returns True if the error is missing function for an assignment in the
    students code.
    """
    _, value, tb = error
    if "module 'exam' has no attribute" in str(value):
        while tb.tb_next:
            tb = tb.tb_next
        filename = tb.tb_frame.f_code.co_filename.split("/")[-1]
        if filename == "test_exam.py":
            return True
    return False


def check_for_tags(*tag_args, default_msg="Does not include any of the given tags"):
    """
    Compares the user tags and the test_case tags to see which tests
    should be be ran.
    """

    def skip_function(msg=default_msg):
        """
        replaces test_cases so they are skipped
        """
        raise SkipTest(msg)

    def decorator(f):
        """Decorator for overwriting test_case functions"""

        @wraps(f)
        def wrapper(self, *args, **kwargs):
            """Wrapper"""
            test_case_tags = set(tag_args)

            if self.SHOW_TAGS:
                return skip_function(
                    f"has the tags: {', '.join(sorted(test_case_tags))}"
                )

            user_tags = set(self.USER_TAGS)
            if user_tags:
                if not user_tags.intersection(test_case_tags):
                    return skip_function()
            return f(self, *args, **kwargs)

        wrapper.__wrapped__ = f  # used to assert that method has been decorated
        return wrapper

    return decorator


def get_testfiles(root=None, extra_assignments=False):
    """
    Gets a list of tuples (path and the testfiles basename) for all
    test_folders.
    """
    base_test_pattern = r"test_(\w)*.py"
    extra_test_pattern = r"extra_test_(\w)*.py"
    pattern = extra_test_pattern if extra_assignments else base_test_pattern

    root_path = Path(root).resolve()
    paths_to_search = [root_path, *root_path.rglob("*")]
    tests = []

    for path in paths_to_search:
        if path.is_file() and re.match(pattern, path.name):
            tests.append((str(path.parent), path.stem))
    return tests


def import_module(proj_path, module_name):
    """
    Loads a module from the given path and name.
    If obligatory_functions is missing Raise exception.
    """
    spec = importer.spec_from_file_location(
        module_name, f"{proj_path}/{module_name}.py"
    )
    module = importer.module_from_spec(spec)

    spec.loader.exec_module(module)
    return module


def find_path_to_assignment(test_file_dir):
    """
    Takes a testfiles location and calculates the path to the assignment,
    given that it has .dbwebb has the same structure as the me folder.
    """
    dir_list = test_file_dir.split("/")
    kmom_index = [i for i, dir in enumerate(dir_list) if dir.startswith("kmom")][0]
    tests_index = kmom_index - 1
    dir_list[tests_index:kmom_index] = ["src"]
    KMOM_AND_ASSIGNENT = "/".join(dir_list)
    return KMOM_AND_ASSIGNENT


def setup_and_get_repo_path(file_dir):
    """
    Change the current working directory to the dir of assignment.
    Returns the path.
    """
    assignment_dir = find_path_to_assignment(file_dir)
    if assignment_dir not in sys.path:
        sys.path.insert(0, assignment_dir)
    try:
        os.chdir(assignment_dir)
    except FileNotFoundError as exc:
        raise MissingDir(assignment_dir) from exc
    return assignment_dir
