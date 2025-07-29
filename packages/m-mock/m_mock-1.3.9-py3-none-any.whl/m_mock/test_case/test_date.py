import unittest

from m_mock import m_random
from m_mock.test_case.common_utils import execute_mock


class TestDate(unittest.TestCase):
    def test_date(self):
        execute_mock("@date('%Y-%m-%d %H:%M:%S', '+1d')")
        execute_mock("@date('%Y-%m-%d %H:%M:%S', '+24h')")
        # 格式化
        execute_mock("@date('%Y年-%m月-%d日 %H时:%M分:%S秒', '+2mon')")
        execute_mock("@date('%Y年-%m月-%d日 %H时:%M分:%S秒', '+2min')")
        print(m_random.m_date.date('%y-%m-%d', '-20d'))
        print(m_random.m_date.date())

    def test_time(self):
        print(m_random.m_date.time('', '+2sec'))
        print(m_random.m_date.time('', '+4sec'))
        execute_mock("@time('', '+4sec')")
        execute_mock("@time")
        execute_mock("@timestamp")

    def test_now(self):
        print(m_random.m_date.now('year'))
        print(m_random.m_date.now('month'))
        print(m_random.m_date.now('week'))
        print(m_random.m_date.now('day'))
        print(m_random.m_date.now('hour'))
        print(m_random.m_date.now('minute'))
        print(m_random.m_date.now('second'))
        execute_mock("@now('year')")
        execute_mock("@now('month')")
        execute_mock("@now('week')")
        execute_mock("@now('day')")
        execute_mock("@now('hour')")
        execute_mock("@now('minute')")
        execute_mock("@now('second')")
        execute_mock("@now()")
        # 格式化
        execute_mock("@now('year','%Y年-%m月-%d日 %H:%M:%S')")
        # 格式化
        execute_mock("@now('week','%Y年 %m月 %d日 %H:%M:%S')")
