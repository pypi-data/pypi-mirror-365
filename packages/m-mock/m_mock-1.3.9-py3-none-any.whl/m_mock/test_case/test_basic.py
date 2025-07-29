import unittest

from m_mock import m_random
from m_mock.test_case.common_utils import execute_mock


class TestBasic(unittest.TestCase):
    def test_basic_character(self):
        print(m_random.m_character.character())
        execute_mock("@character()")
        execute_mock("@character('lower')")
        execute_mock("@character('upper')")
        execute_mock("@character('number')")
        execute_mock("@character('symbol')")
        execute_mock("@character('aeiou')")

    def test_basic_integer(self):
        print(m_random.m_integer.integer())
        execute_mock("@integer(2,4)")
        execute_mock("@integer(3)")
        execute_mock("@integer()")
        # execute_mock("@integer(2,2)")

    def test_basic_boolean(self):
        print(m_random.m_boolean.boolean())
        execute_mock("@boolean(2,4)")
        execute_mock("@boolean(3)")
        execute_mock("@boolean()")
        execute_mock("@boolean(2,2)")

    def test_basic_float(self):
        print(m_random.m_float.float())
        execute_mock("@float(2,4)")
        execute_mock("@float(3)")
        execute_mock("@float()")
        execute_mock("@float(2,2)")

    def test_basic_string(self):
        print(m_random.m_string.string())
        print(m_random.m_string.string(7))
        print(m_random.m_string.string(7, 10))
        execute_mock("@string(2)")
        execute_mock("@string('lower', 3)")
        execute_mock("@string('upper', 3)")
        execute_mock("@string('number', 3)")
        execute_mock("@string('symbol', 3)")
        execute_mock("@string('aeiou', 3)")
        execute_mock("@string('lower', 1, 3)")
        execute_mock("@string('upper', 1, 3)")
        execute_mock("@string('number', 1, 3)")
        execute_mock("@string('symbol', 1, 3)")
        execute_mock("@string('aeiou', 1, 3)")
        execute_mock("@string('chinese', 1, 3)")
        execute_mock("@string('english', 2, 3)")
        execute_mock("@string('cn_symbol', 1, 3)")
        execute_mock("@string('cn_string', 3, 9)")
        execute_mock("@string('cn_string', 1)")
        execute_mock("@string('abcd', 2)")

    def test_text(self):
        execute_mock("@mix_sentence()")
        execute_mock("@csentence()")
        execute_mock("@sentence()")
        execute_mock("@csentence(2,4)")
        execute_mock("@sentence(2,4)")
        execute_mock("@cparagraph()")
        execute_mock("@paragraph()")
        execute_mock("@cparagraph(2,4)")
        execute_mock("@paragraph(2,4)")
