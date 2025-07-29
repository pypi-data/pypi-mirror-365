"""
Use this to test our new and added functionality.
"""

import unittest

from tester import ExamTestCase
from tester.fail_message import FailMessage


class Test_FailMessage_set_answer(unittest.TestCase):
    def setup_empty_examtextcase(self):
        class Test1Assignment1(ExamTestCase):
            def test_a_foo(self):
                "comment"
                pass

        return Test1Assignment1("test_a_foo")

    def test_set_answer_strings(self):
        """
        Answers are strings and called with no options
        Test that special chars in string are excaped
        """
        fail_msg = FailMessage("comment")
        fail_msg.set_answers("\[ 32 m a string\n", "another string")
        self.assertEqual(fail_msg.student_answer, "'\\\\[ 32 m a string\\n'")
        self.assertEqual(fail_msg.correct_answer, "'another string'")

    def test_set_answer_list(self):
        """
        Answers are lists and with no options
        """
        fail_msg = FailMessage("comment")
        fail_msg.set_answers(["a string", 1], ["another string", 3.2, True])
        self.assertEqual(fail_msg.student_answer, "['a string', 1]")
        self.assertEqual(fail_msg.correct_answer, "['another string', 3.2, True]")

    def test_set_answer_strings_norepr(self):
        """
        Called with option norepr
        Test that special chars are not escaped
        """
        fail_msg = FailMessage("comment")
        fail_msg.norepr = True
        fail_msg.set_answers("\[ 32 m a string\n", "another string")
        self.assertEqual(fail_msg.student_answer, "\\[ 32 m a string\n")
        self.assertEqual(fail_msg.correct_answer, "'another string'")

    def test_set_answer_list_two(self):
        """
        Answers are lists and with no options
        """
        fail_msg = FailMessage("comment")
        fail_msg.norepr = True
        fail_msg.set_answers(
            ["a string", 1],
            ["another string", 3.2, True],
        )
        self.assertEqual(fail_msg.student_answer, "['a string', 1]")
        self.assertEqual(fail_msg.correct_answer, "['another string', 3.2, True]")

    def test_set_answer_norepr_clean(self):
        """
        Called with option norepr and that clean works
        """
        fail_msg = FailMessage("comment")
        fail_msg.norepr = True
        fail_msg.set_answers(
            chr(27) + "[2J" + chr(27) + "[;H" + "a string", "another string"
        )
        self.assertEqual(fail_msg.student_answer, "a string")
        self.assertEqual(fail_msg.correct_answer, "'another string'")

    def test_create_fail_msg_no_overrite_what(self):
        fail_msg = FailMessage(
            """
            Testar att funktionen find_all_indexes innehåller try och except konstruktionen.
            Förväntar att följande rad finns i din funktion:
            {correct}
            Din funktion innehåller följande:
            {student}
            """
        )
        fail_msg.student_answer = "a"
        fail_msg.correct_answer = "b"
        correct = [
            "\nTestar att funktionen find_all_indexes innehåller try och except konstruktionen.\n\x1b[40m\x1b[32m\x1b[1mFörväntar att följande rad finns i din funktion:\x1b[0m\nb\n\x1b[40m\x1b[31m\x1b[1mDin funktion innehåller följande:\x1b[0m\na\n"
        ]
        self.assertEqual(fail_msg.create_fail_msg(), correct)

    def test_create_fail_msg_overrite_what(self):
        fail_msg = FailMessage(
            """
            Testar att funktionen find_all_indexes innehåller try och except konstruktionen.
            Förväntar att följande rad finns i din funktion:
            {correct}
            Din funktion innehåller följande:
            {student}
            """
        )
        fail_msg.student_answer = "a"
        fail_msg.correct_answer = "b"
        correct = [
            "\nTestar att funktionen find_all_indexes innehåller try och except konstruktionen.\n\x1b[40m\x1b[32m\x1b[1mChanged correct\x1b[0m\nb\n\x1b[40m\x1b[31m\x1b[1mChanged student\x1b[0m\na\n"
        ]
        fail_msg.what_msgs_from_assert = ["Changed correct", "Changed student"]
        print(fail_msg.create_fail_msg())
        self.assertEqual(fail_msg.create_fail_msg(), correct)


if __name__ == "__main__":
    unitmain(verbosity=2)
