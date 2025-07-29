"""
Tests assertmethods in tester.exam_test_case.py.
"""

import os
import unittest

from tester import ExamTestCase


class Test_ExamTestCase(unittest.TestCase):
    def test_assert_not_in_pass(self):
        """
        Test that assertNotIn works when passing
        """

        class Test1AssertNotIn(ExamTestCase):
            def test_a_foo(self_):
                "comment"
                self_.assertNotIn("correct", ["incorrect"])

        test = Test1AssertNotIn("test_a_foo")
        test.test_a_foo()

        self.assertEqual(test.fail_msg.correct_answer, "'correct'")
        self.assertEqual(test.fail_msg.student_answer, "['incorrect']")

    def test_assert_not_in_fail(self):
        """
        Test that assertNotIn works when failing
        """

        class Test1AssertNotIn(ExamTestCase):
            def test_a_foo(self_):
                "comment"
                self_.assertNotIn("correct", ["correct", "incorrect"])

        test = Test1AssertNotIn("test_a_foo")
        with self.assertRaises(AssertionError):
            test.test_a_foo()

        self.assertEqual(test.fail_msg.correct_answer, "'correct'")
        self.assertEqual(test.fail_msg.student_answer, "['correct', 'incorrect']")

    def test_assert_module_standard_import(self):
        """
        Test that assertModule works for checking import of standard library
        """

        class TestAssertModule(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertModule("random")

        test = TestAssertModule("test_foo")
        test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "'random'")
        self.assertEqual(test.fail_msg.student_answer, "None")

    def test_assert_module_standard_import_fail(self):
        """
        Test that assertModule raise exception for checking import of standard library
        """

        class TestAssertModule(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertModule("random_not_existing")

        test = TestAssertModule("test_foo")
        with self.assertRaises(AssertionError):
            test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "'random_not_existing'")
        self.assertEqual(test.fail_msg.student_answer, "None")

    def test_assert_module_from_path(self):
        """
        Test that assertModule works for checking import from path
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))

        class TestAssertModule(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertModule("__init__", dir_path)

        test = TestAssertModule("test_foo")
        test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "'__init__'")
        self.assertEqual(test.fail_msg.student_answer, repr(dir_path))

    def test_assert_module_from_path_fail(self):
        """
        Test that assertModule raise exception for checking import from path
        """
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/crazy_path"

        class TestAssertModule(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertModule("__init__", dir_path)

        test = TestAssertModule("test_foo")
        with self.assertRaises(AssertionError):
            test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "'__init__'")
        self.assertEqual(test.fail_msg.student_answer, repr(dir_path))

    def test_assert_attribute(self):
        """
        Test that assertAttribute finds function in module
        """

        class TestAssertAttribute(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertAttribute(ExamTestCase, "assertAttribute")

        test = TestAssertAttribute("test_foo")
        test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "'assertAttribute'")
        self.assertEqual(
            test.fail_msg.student_answer,
            "<class 'tester.exam_test_case.ExamTestCase'>",
        )

    def test_assert_attribute_fail(self):
        """
        Test that assertAttribute raise error when module is missing function
        """

        class TestAssertAttribute(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertAttribute(ExamTestCase, "NotAFunction")

        test = TestAssertAttribute("test_foo")
        with self.assertRaises(AssertionError):
            test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "'NotAFunction'")
        self.assertEqual(
            test.fail_msg.student_answer,
            "<class 'tester.exam_test_case.ExamTestCase'>",
        )

    def test_assert_not_attribute(self):
        """
        Test that assertAttribute finds function in module
        """

        class TestAssertNotAttribute(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertNotAttribute(ExamTestCase, "assertDoesNotExist")

        test = TestAssertNotAttribute("test_foo")
        test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "'assertDoesNotExist'")
        self.assertEqual(
            test.fail_msg.student_answer,
            "<class 'tester.exam_test_case.ExamTestCase'>",
        )

    def test_assert_not_attribute_fail(self):
        """
        Test that assertAttribute finds function in module
        """

        class TestAssertNotAttribute(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertNotAttribute(ExamTestCase, "assertNotAttribute")

        test = TestAssertNotAttribute("test_foo")
        with self.assertRaises(AssertionError):
            test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "'assertNotAttribute'")
        self.assertEqual(
            test.fail_msg.student_answer,
            "<class 'tester.exam_test_case.ExamTestCase'>",
        )

    def test_assert_raises(self):
        """
        Test that assertEaises can catch exception
        """

        class TestAssertRaises(ExamTestCase):
            def test_foo(self_):
                "comment"
                with self_.assertRaises(ValueError):
                    raise ValueError()

        test = TestAssertRaises("test_foo")
        test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "<class 'ValueError'>")
        self.assertEqual(test.fail_msg.student_answer, "''")

    def test_assert_raises_other_exception(self):
        """
        Test that assertRaises does not catch other exception
        """

        class TestAssertRaises(ExamTestCase):
            def test_foo(self_):
                "comment"
                with self_.assertRaises(ValueError):
                    self.assertEqual(1, 2)

        test = TestAssertRaises("test_foo")
        with self.assertRaises(AssertionError):
            test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "<class 'ValueError'>")
        self.assertEqual(test.fail_msg.student_answer, "''")

    def test_assert_order_list(self):
        """
        Test that assertOrder for lists
        """

        class TestAssertOrder(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertOrder(["Hej", "haha"], ["Hej", "haha"])

        test = TestAssertOrder("test_foo")
        test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "['Hej', 'haha']")
        self.assertEqual(test.fail_msg.student_answer, "['Hej', 'haha']")

    def test_assert_order_list_str(self):
        """
        Test that assertOrder for string container
        """

        class TestAssertOrder(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertOrder(["Hej", "haha"], "Hej haha")

        test = TestAssertOrder("test_foo")
        test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "['Hej', 'haha']")
        self.assertEqual(test.fail_msg.student_answer, "'Hej haha'")
        self.assertEqual(test.fail_msg.what_msgs_from_assert, [])

    def test_assert_setup_is_called(self):
        """
        Test that assertsetup i called in assert
        """

        class TestAssertOrder(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertOrder(["Hej", "haha"], "Hej haha", ["correct", "student"])

        test = TestAssertOrder("test_foo")
        test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "['Hej', 'haha']")
        self.assertEqual(test.fail_msg.student_answer, "'Hej haha'")
        self.assertEqual(test.fail_msg.what_msgs_from_assert, ["correct", "student"])

    def test_assert_order_fail(self):
        """
        Test that assertOrder raise AttributeError
        """

        class TestAssertOrder(ExamTestCase):
            def test_foo(self_):
                "comment"
                self_.assertOrder(["haha", "Hej"], "Hej haha")

        test = TestAssertOrder("test_foo")
        with self.assertRaises(AssertionError):
            test.test_foo()
        self.assertEqual(test.fail_msg.correct_answer, "['haha', 'Hej']")
        self.assertEqual(test.fail_msg.student_answer, "'Hej haha'")


if __name__ == "__main__":
    # runner = unittest.TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(verbosity=2)
