import unittest

from m_mock.m_random import m_name
from m_mock.test_case.common_utils import execute_mock


class TestName(unittest.TestCase):
    def test_name(self):
        execute_mock("""@clast()""")
        execute_mock("""@cfirst()""")
        execute_mock("""@cname()""")
        execute_mock("""@cname(3)""")
        execute_mock("""@last()""")
        execute_mock("""@first()""")
        execute_mock("""@name()""")
        execute_mock("""@name(True)""")
        print(m_name.cfirst())
        print(m_name.clast())
        print(m_name.cname())
        print(m_name.first())
        print(m_name.last())
        print(m_name.name())
        print(m_name.name(True))

    def test_name2(self):
        for i in range(1000):
            i = m_name.cname()
            assert not '\n' in i
            print(i)
