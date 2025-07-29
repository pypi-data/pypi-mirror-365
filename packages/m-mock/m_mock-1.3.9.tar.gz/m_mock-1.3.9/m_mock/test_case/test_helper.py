import unittest

from m_mock import m_random
from m_mock.test_case.common_utils import execute_mock


class TestHelper(unittest.TestCase):
    def test_helper(self):
        m_random.m_helper.pick('(1,2,3)')
        execute_mock("""@pick('("1",2,"3")')""")
