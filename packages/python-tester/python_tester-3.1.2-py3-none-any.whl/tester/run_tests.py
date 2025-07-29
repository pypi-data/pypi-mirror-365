"""
Custom test collecter, builder and runner used for examining students.
"""

import unittest

from . import sentry
from .cli_parser import parse
from .exam_test_case_exam import ExamTestCaseExam
from .exam_test_result import ExamTestResult
from .exam_test_result_exam import ExamTestResultExam
from .exceptions import ContactError
from .helper_functions import get_testfiles, import_module

PASS = 1
NOT_PASS = 0
RESULT_CLASS = ExamTestResult


def get_testsuites_from_file(path_and_name):
    """
    Create TestSuite with testcases from a file
    """
    path, name = path_and_name
    module = import_module(path, name)

    tl = unittest.TestLoader()

    testsuite = tl.loadTestsFromModule(module)
    return testsuite


def build_testsuite(ARGS):
    """
    Create TestSuit with testcases.
    """
    global RESULT_CLASS
    all_suites = unittest.TestSuite()

    for path_and_name in sorted(get_testfiles(ARGS.tests, ARGS.extra_assignments)):
        filesuites = get_testsuites_from_file(path_and_name)
        for suite in filesuites:
            for case in suite:
                case.USER_TAGS = ARGS.tags
                case.SHOW_TAGS = ARGS.show_tags
                #  under nog vara en bugg. har inte testa om det funkar med Exam tester då vi använder det längre
                if issubclass(type(case), ExamTestCaseExam):
                    RESULT_CLASS = ExamTestResultExam
            all_suites.addTest(suite)
    return all_suites


def run_testcases(suite, ARGS):
    """
    Run testsuit.
    """
    runner = unittest.TextTestRunner(
        resultclass=RESULT_CLASS,
        verbosity=2,
        failfast=not ARGS.failslow,
        descriptions=False,
    )

    try:
        results = runner.run(suite)
    except Exception as e:
        raise ContactError() from e

    return results


def main():
    """
    Start point of program.
    """
    ARGS = parse()

    if ARGS.sentry:
        sentry.activate_sentry(
            ARGS.sentry_url,
            ARGS.sentry_release,
            ARGS.sentry_sample_rate,
            ARGS.sentry_user,
            ARGS.tests,
        )

    suite = build_testsuite(ARGS)
    results = run_testcases(suite, ARGS)
    results.exit_with_result()


if __name__ == "__main__":
    main()
