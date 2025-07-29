"""
Use this to test our new and added functionality.
"""

import unittest
from unittest import SkipTest

from tester import ExamTestCase, tags
from tester import exceptions as exce


class Test_ExamTestCase(unittest.TestCase):
    def setup_empty_examtextcase(self):
        class Test1Assignment1(ExamTestCase):
            def test_a_foo(self):
                "comment"
                pass

        return Test1Assignment1("test_a_foo")

    def test_set_test_name_and_assignment(self):
        """
        Tests that set_test_name_and_assignment extracts test name and assignment
        correct.
        """

        class Test1Assignment1(ExamTestCase):
            link_to_assignment = "a link"

            def test_a_foo(self):
                "comment"
                pass

        test = Test1Assignment1("test_a_foo")
        self.assertEqual(test.assignment, "Assignment1")
        self.assertEqual(test.test_name, "foo")
        self.assertEqual(test.link_to_assignment, "a link")

    def test_set_assignment_only_a_letter_for_func_name(self):
        """
        Tests that set_test_name_and_assignment work for only a letter after test_.
        """

        class Test2Assignment1(ExamTestCase):
            def test_a(self):
                "comment"
                pass

        test = Test2Assignment1("test_a")
        self.assertEqual(test.assignment, "Assignment1")
        self.assertEqual(test.test_name, "a")
        self.assertEqual(test.link_to_assignment, "")

    def test_set_assignment_rasie_exception_missing_letter(self):
        """
        Tests that set_test_name_and_assignment raise ValueError when test function
        miss letter.
        """

        class Test1Assignment1(ExamTestCase):
            def test_foo(self):
                "comment"
                pass

        test = Test1Assignment1("test_foo")
        self.assertEqual(test.assignment, "Assignment1")
        self.assertEqual(test.test_name, "foo")

    def test_set_assignment_rasie_exception_missing_Upper_letter(self):
        """
        Tests that set_test_name_and_assignment raise ValueError when class name
        miss word that start with uppercase letter.
        """

        class Test1assignment(ExamTestCase):
            def test_a_foo(self):
                "comment"
                pass

        with self.assertRaises(exce.TestClassNameError) as cxt:
            test = Test1assignment("test_a_foo")

    def test_set_assignment_rasie_exception_missing_number(self):
        """
        Tests that set_test_name_and_assignment raise ValueError when class name
        miss start number.
        """

        class TestAssignment1(ExamTestCase):
            def test_a_foo(self):
                "comment"
                pass

        test = TestAssignment1("test_a_foo")
        self.assertEqual(test.assignment, "Assignment1")
        self.assertEqual(test.test_name, "foo")

    def test_set_assignment_works_without_number_after(self):
        """
        Tests that set_test_name_and_assignment work with number after word.
        """

        class Test1Assignment(ExamTestCase):
            def test_a_foo(self):
                "comment"
                pass

        test = Test1Assignment("test_a_foo")
        self.assertEqual(test.assignment, "Assignment")
        self.assertEqual(test.test_name, "foo")

    def test_set_assignment_works_with_multiple_words(self):
        """
        Tests that set_test_name_and_assignment work with multiple words.
        """

        class Test4ModulesExist(ExamTestCase):
            def test_a_foo(self):
                "comment"
                pass

        test = Test4ModulesExist("test_a_foo")
        self.assertEqual(test.assignment, "ModulesExist")
        self.assertEqual(test.test_name, "foo")

    def test_skip_test_by_tags(self):
        """
        Tests that SkipTest is raised when the tags does not match.
        """

        class Test1Tags1(ExamTestCase):
            USER_TAGS = ["dont_skip"]

            @tags("skip")
            def test_a_foo(self):
                "comment"
                self.assertEqual("correct", "incorrect")

        test = Test1Tags1("test_a_foo")

        with self.assertRaises(SkipTest) as _:
            test.test_a_foo()
        # check that method was decorated for tags
        self.assertEqual(getattr(test.test_a_foo, "__wrapped__").__name__, "test_a_foo")

    def test_show_tags_for_test(self):
        """
        Tests that SkipTest is raised and it prints tags when SHOW_TAGS is set.
        """

        class Test1Tags1(ExamTestCase):
            SHOW_TAGS = True

            @tags("skip", "no_skip")
            def test_a_foo(self):
                "comment"
                self.assertEqual("correct", "incorrect")

        test = Test1Tags1("test_a_foo")

        with self.assertRaises(SkipTest) as e:
            test.test_a_foo()

        self.assertEqual("has the tags: no_skip, skip", str(e.exception))

        # check that method was decorated for tags
        self.assertEqual(getattr(test.test_a_foo, "__wrapped__").__name__, "test_a_foo")

    def test_run_test_by_tags(self):
        """
        Tests that an overwritten test runs the test without being skipped.
        """

        class Test1Tags1(ExamTestCase):
            USER_TAGS = ["dont_skip"]

            @tags("dont_skip")
            def test_a_foo(self):
                "comment"
                return "Not Skipped"

        test = Test1Tags1("test_a_foo")
        self.assertEqual(test.test_a_foo(), "Not Skipped")
        # check that method was decorated for tags
        self.assertEqual(getattr(test.test_a_foo, "__wrapped__").__name__, "test_a_foo")

    def test_skip_test_when_error(self):
        """
        Tests that SkipTest is raised when tested code raise an exception.
        This was a bug before.
        """

        class Test1Tags1(ExamTestCase):
            USER_TAGS = ["dont_skip"]

            @tags("skip")
            def test_a_foo(self):
                "comment"
                raise KeyError()

        test = Test1Tags1("test_a_foo")

        with self.assertRaises(SkipTest) as _:
            test.test_a_foo()

    def test_passing_simpel_test(self):
        """
        Check that a normal test works
        """

        class Test1Simpel(ExamTestCase):
            def test_a_foo(self):
                "comment"
                self.assertEqual("hej", "hej")

        test = Test1Simpel("test_a_foo")
        self.assertEqual(test.USER_TAGS, [])

    def test_wrapped_tags_correct_metadata(self):
        """
        Check that a tags-wrapped test has its own metadata and not wrapped functions
        """

        class Test1Simpel(ExamTestCase):
            @tags("test")
            def test_a_foo(self):
                """a comment"""
                "comment"
                self.assertEqual("hej", "hej")

        test = Test1Simpel("test_a_foo")
        self.assertEqual(test._testMethodDoc, "a comment")


if __name__ == "__main__":
    # runner = unittest.TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(verbosity=2)
