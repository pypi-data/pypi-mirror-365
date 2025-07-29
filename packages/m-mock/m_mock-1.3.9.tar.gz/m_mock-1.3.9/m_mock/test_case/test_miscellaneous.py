import unittest

from m_mock import m_random

from m_mock.test_case.common_utils import execute_mock


class TestMiscellaneous(unittest.TestCase):
    def test_id(self):
        execute_mock("""@id()""")
        execute_mock("""@increment()""")
        execute_mock("""@increment(100)""")
        execute_mock("""@uuid()""")
        print(m_random.m_miscellaneous.increment())

