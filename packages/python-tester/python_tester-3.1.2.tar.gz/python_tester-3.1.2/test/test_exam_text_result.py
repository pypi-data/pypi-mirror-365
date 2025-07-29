"""
Use this to test our new and added functionality.
"""

import sys
import unittest
from unittest.runner import _WritelnDecorator

from tester import ExamTestCase, ExamTestResult


class Test_TestResult(unittest.TestCase):
    def test_startTest(self):
        """
        Tests the overshadowed method `startTest`.
        TODO:
            - Also test the output? of "self.stream"?
        """

        class Test1Assignment1(ExamTestCase):
            def test_a_foo(self):
                "comment"
                pass

        test = Test1Assignment1("test_a_foo")
        result = ExamTestResult(_WritelnDecorator(sys.stderr), True, 2)

        result.startTest(test)

        self.assertEqual(test.assignment, "Assignment1")
        self.assertEqual(test.test_name, "foo")

        self.assertIn("Assignment1", result.assignments_results)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        result.stopTest(test)

    def test_name_not_correct_raise_except(self):
        """
        Tests that except is raise when test function name is wrong.
        """
        # no longer valid as moved functionality - keeping to see example of how to test class
        # class Foo(unittest.TestCase):
        #     def test_1(self):
        #         pass
        #
        # test = Foo('test_1')
        # result = ExamTestResult(_WritelnDecorator(sys.stderr), True, 2)
        #
        # with self.assertRaises(ValueError) as cxt:
        #     result.startTest(test)
        #
        # result.stopTest(test)


if __name__ == "__main__":
    # runner = unittest.TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(verbosity=2)
