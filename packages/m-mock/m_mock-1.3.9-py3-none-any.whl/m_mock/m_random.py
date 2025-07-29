import random
import re
import string
import uuid
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Union, Optional, List, Tuple

from m_mock.m_random_source import single_family_name, en_family_name, en_name, chinese, cn_punctuation


def in_none(obj: Union[tuple, list, str, None]) -> bool:
    """
    检查对象是否为空或None

    :param obj: 要检查的对象(可以是元组/列表/字符串/None)
    :return: 如果对象为空/None返回True，否则返回False
    """
    if isinstance(obj, (tuple, list)):
        return all(i in ('', None) for i in obj)
    return obj in ('', None)


def tuple_to_str(objects: Union[tuple, list]) -> str:
    """
    将元组/列表转换为字符串

    :param objects: 要转换的元组/列表
    :return: 转换后的字符串
    """
    return ''.join(objects)


def shuffle_string(strings: Union[str, list, tuple]) -> str:
    """
    打乱字符串或序列中的字符

    :param strings: 要打乱的输入(字符串/列表/元组)
    :return: 打乱后的字符串
    """
    if isinstance(strings, str):
        strings = list(strings)
    random.shuffle(strings)
    return ''.join(strings)


class MockPyExpressionException(Exception):
    """
    模拟表达式错误的自定义异常类
    """

    def __init__(self, exception: str = '使用了错误的模拟器表达式', remark: Optional[str] = None):
        super().__init__()
        self.exception = f'{exception}{remark or ""}'

    def __str__(self) -> str:
        return self.exception

    @classmethod
    def min_max_value_exception(cls, min_value: Optional[int], max_value: Optional[int]) -> None:
        """
        验证最小/最大值

        :param min_value: 最小值
        :param max_value: 最大值
        :raises MockPyExpressionException: 如果最小值 >= 最大值
        """
        if min_value is not None and max_value is not None and min_value >= max_value:
            raise cls('最小值不能大于或等于最大值')


_mock_exception = MockPyExpressionException()


class BooleanM:
    """
    布尔值生成器
    """

    @classmethod
    def boolean(cls, min_value: Optional[int] = None, max_value: Optional[int] = None,
                current: Optional[bool] = None) -> bool:
        """
        生成一个布尔值

        :param min_value: 最小值(默认0)
        :param max_value: 最大值(默认1)
        :param current: 当前值(默认True)
        :return: 生成的布尔值
        """
        _mock_exception.min_max_value_exception(min_value, max_value)

        if in_none((max_value, current)) and not in_none(min_value):
            return True

        min_value = 0 if in_none(min_value) else min_value
        max_value = 1 if in_none(max_value) else max_value
        current = True if in_none(current) else current

        return current if random.randint(min_value, max_value) == min_value else not current


m_boolean = BooleanM()


class NaturalM:
    """
    自然数生成器
    """

    @classmethod
    def natural(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        """
        生成一个自然数

        :param min_value: 最小值(默认0)
        :param max_value: 最大值(默认9999999999999999)
        :return: 随机自然数
        """
        min_value = 0 if in_none(min_value) else min_value
        max_value = 9999999999999999 if in_none(max_value) else max_value
        _mock_exception.min_max_value_exception(min_value, max_value)
        return random.randint(min_value, max_value)


m_natural = NaturalM()


class NumberM:
    """
    数字字符串生成器
    """
    number_str_max_length = None

    @classmethod
    def number_str(cls, min_length: Optional[int] = None, max_length: Optional[int] = None) -> str:
        """
        生成随机长度的数字字符串

        :param min_length: 最小长度
        :param max_length: 最大长度
        :return: 随机数字字符串
        """
        _mock_exception.min_max_value_exception(max_length, min_length)
        min_length = random.randint(0, 15) if in_none(min_length) else min_length
        max_length = random.randint(min_length, 16) if in_none(max_length) else max_length

        range_size = cls.number_not_start_with_zero(min_length, max_length)
        return ''.join(str(random.randint(0, 9)) for _ in range(range_size))

    @classmethod
    def number_not_start_with_zero(cls, start_number: int, end_number: int) -> int:
        """
        生成不以零开头的随机数

        :param start_number: 最小值(包含)
        :param end_number: 最大值(包含)
        :return: start_number和end_number之间的随机整数
        """
        start = start_number if start_number != 0 else 1
        end = end_number if end_number != 1 else 2
        return random.randint(start, end)


m_number = NumberM()


class IntegerM:
    """
    整数生成器
    """

    @classmethod
    def integer(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        """
        生成随机整数

        :param min_value: 最小值(默认-9999999999999999)
        :param max_value: 最大值(默认9999999999999999)
        :return: 随机整数
        """
        _mock_exception.min_max_value_exception(min_value, max_value)
        min_value = -9999999999999999 if in_none(min_value) else min_value
        max_value = 9999999999999999 if in_none(max_value) else max_value
        return random.randint(min_value, max_value)


m_integer = IntegerM()


class CharacterM:
    """
    字符生成器
    """

    @classmethod
    def character(cls, character_type: Optional[str] = None) -> str:
        """
        生成随机字符

        :param character_type: 字符类型(小写/大写/数字/符号)
        :return: 随机字符
        """
        if character_type is None:
            character_type = random.choice(('lower', 'upper', 'number', 'symbol'))
        return StringM.string(character_type, 1)


m_character = CharacterM()


class FloatM:
    """
    浮点数生成器
    """

    @classmethod
    def float(cls, min_value: Optional[float] = None, max_value: Optional[float] = None,
              d_min_value: Optional[int] = None, d_max_value: Optional[int] = None) -> float:
        """
        生成随机浮点数

        :param min_value: 整数部分最小值
        :param max_value: 整数部分最大值
        :param d_min_value: 最小小数位数
        :param d_max_value: 最大小数位数
        :return: 随机浮点数
        """

        def __luck() -> bool:
            """75%概率返回True"""
            return random.randint(1, 4) in (1, 2, 3)

        _mock_exception.min_max_value_exception(min_value, max_value)

        min_value = -9999999999999999 if in_none(min_value) else min_value
        max_value = 9999999999999999 if in_none(max_value) else max_value

        if in_none(d_min_value):
            d_min_value = random.randint(2, 5) if __luck() else 0

        if in_none(d_max_value):
            min_d_max_value = d_min_value if 0 < d_min_value < 14 else d_min_value + 1
            d_max_value = random.randint(min_d_max_value + 1, 16)

        decimals = StringM.string_number(d_min_value, d_max_value)

        if __luck():
            while True:
                random_float = random.uniform(min_value, max_value)
                val = str(random_float)
                if '.' in val:
                    break
            int_part = val.split(".")[0]
            int_part = int_part if len(int_part) + len(decimals) <= 15 else int_part[:15 - len(decimals)]
            random_float = float(f'{int_part}.{decimals}')
        else:
            random_float = random.uniform(min_value, max_value)
            if __luck():
                random_float = float(f'{str(random_float)[:-1]}{random.randint(1, 9)}')

        return float(round(random_float, random.randint(d_min_value, d_max_value)))


m_float = FloatM()


class StringM:
    """
    多种类型的字符串生成器
    """

    @classmethod
    def get_random_string_by_source(cls, source: str, min_value: Optional[int] = None,
                                    max_value: Optional[int] = None) -> str:
        """
        从给定源生成随机字符串

        :param source: 字符源
        :param min_value: 最小长度
        :param max_value: 最大长度
        :return: 随机字符串
        """
        _mock_exception.min_max_value_exception(min_value, max_value)

        if in_none(min_value):
            length = random.randint(1, 9)
        elif in_none(max_value):
            length = min_value
        else:
            length = random.randint(min_value, max_value)

        chars = [random.choice(source) for _ in range(length)]
        random.shuffle(chars)
        return ''.join(chars)

    @classmethod
    def string_lower(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> str:
        """生成随机小写字符串"""
        return cls.get_random_string_by_source(string.ascii_lowercase, min_value, max_value)

    @classmethod
    def string_upper(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> str:
        """生成随机大写字符串"""
        return cls.get_random_string_by_source(string.ascii_uppercase, min_value, max_value)

    @classmethod
    def string_number(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> str:
        """生成随机数字字符串"""
        return cls.get_random_string_by_source(string.digits, min_value, max_value)

    @classmethod
    def string_symbol(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> str:
        """生成随机符号字符串"""
        return cls.get_random_string_by_source(string.punctuation, min_value, max_value)

    @classmethod
    def strings(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> str:
        """生成包含(英文/数字/符号)的随机长度字符串"""
        source = string.ascii_letters + string.digits + string.punctuation
        return cls.get_random_string_by_source(source, min_value, max_value)

    @classmethod
    def chinese(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> str:
        """生成随机中文字符串"""
        min_value = 1 if in_none(min_value) else min_value
        return cls.get_random_string_by_source(chinese, min_value, max_value)

    @classmethod
    def english(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> str:
        """生成随机英文字符串"""
        min_value = 1 if in_none(min_value) else min_value
        return cls.get_random_string_by_source(string.ascii_letters, min_value, max_value)

    @classmethod
    def cn_symbol(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> str:
        """生成随机中文标点符号字符串"""
        return cls.get_random_string_by_source(cn_punctuation, min_value, max_value)

    @classmethod
    def cn_string(cls, min_value: Optional[int] = None, max_value: Optional[int] = None) -> str:
        """生成随机中文字符串(包含中文标点符号)"""

        def __cn_sting() -> str:
            cn_min_value = random.randint(1, max_value - 1)
            cn_str = cls.get_random_string_by_source(chinese, cn_min_value)
            cn_sym = cls.cn_symbol(max_value - cn_min_value)
            combined = list(cn_str + cn_sym)
            random.shuffle(combined)
            return ''.join(combined)

        if min_value is not None and min_value >= 2 and in_none(max_value):
            max_value = min_value
            return __cn_sting()
        elif in_none(max_value) or min_value == 1:
            return cls.get_random_string_by_source(cn_punctuation + chinese, min_value, max_value)
        return __cn_sting()

    @classmethod
    def string(cls, *args) -> Optional[str]:
        """
        根据类型生成随机字符串

        :param args: 类型和长度参数
        :return: 随机字符串或None(如果无效)
        """
        if len(args) <= 1 or isinstance(args[0], int):
            return cls.strings(*args)
        elif 2 <= len(args) <= 3:
            string_type = args[0]
            new_args = args[1:]

            generators = {
                'lower': cls.string_lower,
                'upper': cls.string_upper,
                'number': cls.string_number,
                'symbol': cls.string_symbol,
                'string': cls.strings,
                'chinese': cls.chinese,
                'english': cls.english,
                'cn_symbol': cls.cn_symbol,
                'cn_string': cls.cn_string
            }

            if string_type in generators:
                return generators[string_type](*new_args)
            return cls.get_random_string_by_source(string_type, *new_args)
        elif len(args) > 3:
            raise MockPyExpressionException('最多只允许3个参数')
        return None


m_string = StringM()


class DateM:
    """
    日期和时间生成器
    """

    @classmethod
    def datetime_calculate(cls, date_time: datetime, time_interval: str, format_str: Optional[str]) -> Optional[str]:
        """
        基于时间间隔计算日期时间

        :param date_time: 基准日期时间
        :param time_interval: 时间间隔(例如'+1min')
        :param format_str: 输出格式
        :return: 格式化后的日期时间字符串或None
        """
        calculate = time_interval[:1]
        unit = re.search('[a-zA-Z]+', time_interval).group(0)
        amount = int(time_interval[1:-len(unit)])

        if 'hours'.startswith(unit):
            delta = timedelta(hours=amount)
        elif 'minutes'.startswith(unit):
            delta = timedelta(minutes=amount)
        elif 'milliseconds'.startswith(unit):
            delta = timedelta(milliseconds=amount)
        elif 'microseconds'.startswith(unit):
            delta = timedelta(microseconds=amount)
        elif 'seconds'.startswith(unit):
            delta = timedelta(seconds=amount)
        elif 'days'.startswith(unit):
            delta = timedelta(days=amount)
        elif 'month'.startswith(unit):
            return (date_time + relativedelta(months=amount)).strftime(format_str)
        elif 'week'.startswith(unit):
            return (date_time + relativedelta(weeks=amount)).strftime(format_str)
        else:
            return None

        if calculate == '+':
            return (date_time + delta).strftime(format_str)
        elif calculate == '-':
            return (date_time - delta).strftime(format_str)
        return None

    @classmethod
    def datetime(cls, format_str: Optional[str] = None, time_interval: Optional[str] = None) -> str:
        """
        生成格式化日期时间字符串

        :param format_str: 格式字符串(默认'%Y-%m-%d %H:%M:%S')
        :param time_interval: 时间间隔(例如'+1min')
        :return: 格式化后的日期时间字符串
        :raises MockPyExpressionException: 无效的时间间隔
        """
        if time_interval and (len(time_interval) <= 1 or time_interval[:1] not in ('+', '-')):
            raise MockPyExpressionException(remark="正确的时间表达式应为'+1h'或'-1h'")

        curr_time = datetime.now()
        if time_interval:
            return cls.datetime_calculate(curr_time, time_interval, format_str or '%Y-%m-%d %H:%M:%S')
        return curr_time.strftime(format_str or '%Y-%m-%d %H:%M:%S')

    @classmethod
    def date(cls, format_str: Optional[str] = None, time_interval: Optional[str] = None) -> str:
        """
        生成格式化日期字符串

        :param format_str: 格式字符串(默认'%Y-%m-%d')
        :param time_interval: 时间间隔(例如'-1d')
        :return: 格式化后的日期字符串
        """
        return cls.datetime(format_str or '%Y-%m-%d', time_interval)

    @classmethod
    def timestamp(cls) -> int:
        """生成当前时间戳(毫秒)"""
        return int(datetime.now().timestamp() * 1000)

    @classmethod
    def time(cls, format_str: Optional[str] = None, time_interval: Optional[str] = None) -> str:
        """
        生成格式化时间字符串

        :param format_str: 格式字符串(默认'%H:%M:%S')
        :param time_interval: 时间间隔(例如'-1h')
        :return: 格式化后的时间字符串
        """
        return cls.datetime(format_str or '%H:%M:%S', time_interval)

    @staticmethod
    def get_current_week(date: Optional[str] = None, format_str: str = '%Y-%m-%d') -> Tuple[str, str]:
        """
        获取当前周的周一和周日日期

        :param date: 日期字符串(可选)
        :param format_str: 格式字符串
        :return: (周一, 周日)日期元组
        """
        duty_date = datetime.strptime(date, format_str) if date else datetime.today()
        monday = sunday = duty_date
        one_day = timedelta(days=1)

        while monday.weekday() != 0:
            monday -= one_day
        while sunday.weekday() != 6:
            sunday += one_day

        return monday.strftime(format_str), sunday.strftime(format_str)

    @classmethod
    def now(cls, unit: Optional[str] = None, format_str: str = '%Y-%m-%d %H:%M:%S') -> Optional[str]:
        """
        获取指定单位的当前日期时间

        :param unit: 时间单位(年/月/周/日/时/分/秒)
        :param format_str: 格式字符串
        :return: 格式化后的日期时间字符串或None
        """
        default_format = '%Y-%m-%d %H:%M:%S'
        now = cls.date(format_str='%Y') + '-01-01 00:00:00'

        unit_map = {
            'year': lambda: datetime.strptime(now, default_format).strftime(format_str),
            'month': lambda: datetime.strptime(cls.date(format_str='%Y-%m') + '-01 00:00:00',
                                               default_format).strftime(format_str),
            'week': lambda: datetime.strptime(cls.get_current_week()[1] + ' 00:00:00',
                                              default_format).strftime(format_str),
            'day': lambda: datetime.strptime(cls.date(format_str='%Y-%m-%d') + ' 00:00:00',
                                             default_format).strftime(format_str),
            'hour': lambda: datetime.strptime(cls.date(format_str='%Y-%m-%d  %H') + ':00:00',
                                              default_format).strftime(format_str),
            'minute': lambda: datetime.strptime(cls.date(format_str='%Y-%m-%d  %H:%M') + ':00',
                                                default_format).strftime(format_str),
            'second': lambda: cls.datetime(format_str=format_str),
            None: lambda: cls.datetime(format_str=format_str)
        }

        return unit_map.get(unit, lambda: None)()


m_date = DateM()


class HelperM:
    """
    辅助函数
    """

    @classmethod
    def pick(cls, pick_list: Union[str, list, tuple]) -> Union[str, int, float]:
        """
        从列表中随机选择一个元素

        :param pick_list: 要选择的列表
        :return: 随机元素
        :raises MockPyExpressionException: 空输入
        """
        if in_none(pick_list):
            raise MockPyExpressionException('pick_list不能为空')
        if isinstance(pick_list, str):
            pick_list = eval(pick_list)
        return random.choice(pick_list)


m_helper = HelperM()


class NameM:
    """
    姓名生成器
    """

    @classmethod
    def first(cls) -> str:
        """获取随机英文姓氏"""
        return random.choice(en_family_name)

    @classmethod
    def last(cls) -> str:
        """获取随机英文名字"""
        return random.choice(en_name)

    @classmethod
    def name(cls, middle: Optional[Union[str, bool, int]] = None) -> str:
        """
        生成英文姓名

        :param middle: 是否包含中间名
        :return: 英文姓名字符串
        """
        if middle and str(middle).lower() in ('true', '1'):
            first = cls.first()
            last = cls.last()
            for _ in range(20):  # 尝试找到不同的中间名
                mid = cls.first()
                if mid != first:
                    return f'{first} {mid} {last}'
            return f'{first} {last} {last}'  # 如果找不到不同的中间名则回退
        return f'{cls.first()} {cls.last()}'

    @classmethod
    def cfirst(cls, length: Optional[int] = None) -> str:
        """
        生成随机中文名字

        :param length: 名字长度(1-3)
        :return: 中文名字字符串
        :raises MockPyExpressionException: 无效的长度
        """
        length = random.randint(1, 3) if length is None else length
        if not 1 <= length <= 3:
            raise MockPyExpressionException('无效的名字长度')
        return m_string.chinese(length, length + 1)[:length]

    @classmethod
    def clast(cls) -> str:
        """获取随机中文姓氏"""
        return random.choice(single_family_name)

    @classmethod
    def cname(cls, length: Optional[int] = None) -> str:
        """
        生成中文全名

        :param length: 名字长度(2-3)
        :return: 中文全名
        :raises MockPyExpressionException: 无效的长度
        """
        length = random.randint(2, 3) if length is None else length
        if not 2 <= length <= 3:
            raise MockPyExpressionException('无效的名字长度')
        return cls.clast() + cls.cfirst(length - 1)


m_name = NameM()


class MiscellaneousM:
    """
    杂项生成器
    """
    increment_start = 0

    @classmethod
    def uuid(cls) -> str:
        """生成随机UUID"""
        return str(uuid.uuid4())

    @classmethod
    def id(cls) -> str:
        """生成随机中国身份证号"""
        return cls.generate_random_id()

    @classmethod
    def increment(cls, step: Optional[int] = None) -> str:
        """
        自增计数器

        :param step: 增量步长(默认1)
        :return: 自增后的值(字符串形式)
        """
        step = 1 if step is None else step
        cls.increment_start += step
        return f"{cls.increment_start}"

    @staticmethod
    def get_random_date(start_year: int = 1960, end_year: int = 2020) -> str:
        """生成随机出生日期"""
        start = datetime(start_year, 1, 1).date()
        end = datetime(end_year, 12, 31).date()
        days_between = (end - start).days
        random_days = random.randrange(days_between)
        return (start + timedelta(days=random_days)).strftime("%Y%m%d")

    @staticmethod
    def calculate_checksum(id17: str) -> str:
        """计算身份证校验码"""
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        checksums = '10X98765432'
        sum_product = sum(int(id17[i]) * weights[i] for i in range(17))
        return checksums[sum_product % 11]

    @classmethod
    def generate_random_id(cls) -> str:
        """生成随机中国身份证号码"""
        region_code = str(random.randint(100000, 699999))  # 随机地区码
        birth_date = cls.get_random_date()  # 随机出生日期
        sequence_code = str(random.randint(0, 999)).zfill(3)  # 随机顺序码
        id17 = region_code + birth_date + sequence_code  # 组成前17位
        checksum = cls.calculate_checksum(id17)  # 计算校验码
        return f"{id17}{checksum}"  # 完整身份证号


m_miscellaneous = MiscellaneousM()


class TextM:
    """
    文本生成器
    """

    @classmethod
    def paragraph(cls, min_sentences: int = 3, max_sentences: int = 10) -> str:
        """
        生成英文段落

        :param min_sentences: 最小句子数
        :param max_sentences: 最大句子数
        :return: 英文段落
        """
        num = random.randint(min_sentences, max_sentences)
        pick_list = [',', '!', '?']
        sentences = [f'{m_string.english(1, 10)[:-1]}{random.choice(pick_list)}' for _ in range(num)]
        return f"{''.join(sentences)[:-1]}."

    @classmethod
    def cparagraph(cls, min_sentences: int = 3, max_sentences: int = 10) -> str:
        """
        生成中文段落

        :param min_sentences: 最小句子数
        :param max_sentences: 最大句子数
        :return: 中文段落
        """
        num = random.randint(min_sentences, max_sentences)
        pick_list = ['，', '！', '？']
        sentences = [f'{m_string.chinese(1, 10)[:-1]}{random.choice(pick_list)}' for _ in range(num)]
        return f"{''.join(sentences)[:-1]}。"

    @classmethod
    def sentence(cls, min_words: int = 3, max_words: int = 10) -> str:
        """
        生成英文句子

        :param min_words: 最小单词数
        :param max_words: 最大单词数
        :return: 英文句子
        """
        return f"{m_string.english(min_words, max_words)}."

    @classmethod
    def csentence(cls, min_words: int = 3, max_words: int = 10) -> str:
        """
        生成中文句子

        :param min_words: 最小词数
        :param max_words: 最大词数
        :return: 中文句子
        """
        return f"{m_string.chinese(min_words, max_words)}。"

    @classmethod
    def mix_sentence(cls, min_words: int = 1, max_words: int = 10) -> str:
        """
        生成混合语言句子

        :param min_words: 最小词数
        :param max_words: 最大词数
        :return: 混合语言句子
        """
        parts = [
            cls.sentence(min_words, max_words),
            cls.csentence(min_words, max_words),
            m_string.string_number(min_words, max_words)
        ]
        return shuffle_string(''.join(parts))


m_text = TextM()
