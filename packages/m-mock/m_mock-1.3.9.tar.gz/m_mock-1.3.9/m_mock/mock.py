import re
from m_mock import m_random


class MockM:
    """
    模拟数据生成器核心类

    通过关键字映射调用对应的随机数据生成方法
    """

    def __init__(self):
        # 创建关键字映射字典，将关键字关联到对应的模块和方法
        self.keyword_mapping = {
            # 日期时间相关
            'date': (m_random.m_date, 'date'),
            'datetime': (m_random.m_date, 'datetime'),
            'time': (m_random.m_date, 'time'),
            'timestamp': (m_random.m_date, 'timestamp'),
            'now': (m_random.m_date, 'now'),

            # 数字相关
            'float': (m_random.m_float, 'float'),
            'natural': (m_random.m_natural, 'natural'),
            'integer': (m_random.m_integer, 'integer'),
            'boolean': (m_random.m_boolean, 'boolean'),

            # 字符串相关
            'character': (m_random.m_character, 'character'),
            'string': (m_random.m_string, 'string'),

            # 辅助功能
            'pick': (m_random.m_helper, 'pick'),
            'increment': (m_random.m_miscellaneous, 'increment'),

            # 中文姓名相关
            'cfirst': (m_random.m_name, 'cfirst'),
            'clast': (m_random.m_name, 'clast'),
            'cname': (m_random.m_name, 'cname'),

            # 英文姓名相关
            'first': (m_random.m_name, 'first'),
            'last': (m_random.m_name, 'last'),
            'name': (m_random.m_name, 'name'),

            # 标识符相关
            'id': (m_random.m_miscellaneous, 'id'),
            'uuid': (m_random.m_miscellaneous, 'uuid'),

            # 文本相关
            'mix_sentence': (m_random.m_text, 'mix_sentence'),
            'sentence': (m_random.m_text, 'sentence'),
            'csentence': (m_random.m_text, 'csentence'),
            'paragraph': (m_random.m_text, 'paragraph'),
            'cparagraph': (m_random.m_text, 'cparagraph'),
        }

    def mock(self, mock_str: str) -> any:
        """
        根据输入字符串生成模拟数据

        :param mock_str: 模拟字符串表达式，如"@date()"、"@name()"
        :return: 生成的模拟数据
        :raises MockPyExpressionException: 当表达式格式错误时抛出
        """
        # 1. 提取关键字
        keyword = self.get_mocker_key(mock_str)

        # 2. 提取参数
        args = self.get_mocker_params_to_tuple(mock_str)

        # 3. 通过关键字获取对应的模块和方法
        module_method_pair = self.keyword_mapping.get(keyword)

        if module_method_pair:
            module, method_name = module_method_pair
            try:
                # 4. 动态调用对应方法并传入参数
                return getattr(module, method_name)(*args)
            except Exception as e:
                raise m_random.MockPyExpressionException(f"调用方法失败: {method_name}, 错误: {str(e)}")
        else:
            # 5. 如果没有匹配的关键字，返回原始字符串
            return mock_str

    @classmethod
    def get_mocker_key(cls, mock_str: str) -> str:
        """
        从模拟字符串中提取关键字

        :param mock_str: 模拟字符串，如"@date()"、"@name"
        :return: 提取的关键字，如"date"、"name"
        :raises MockPyExpressionException: 当字符串不以@开头时抛出
        """
        if not mock_str.startswith('@'):
            raise m_random.MockPyExpressionException("模拟表达式必须以@开头")

        # 如果不是以括号结尾，直接返回@后的内容
        if not mock_str.endswith(')'):
            return mock_str[1:]

        # 使用正则提取@和(之间的内容
        regular = r'(?<=(@)).*?(?=\()'
        match = re.search(regular, mock_str)
        if not match:
            raise m_random.MockPyExpressionException("无法提取关键字")
        return match.group(0)

    @classmethod
    def get_mocker_params_to_tuple(cls, mock_params: str) -> tuple:
        """
        将模拟参数转换为元组形式

        :param mock_params: 参数字符串，如"('%Y.%m.%d %H:%M:%S','+1')"
        :return: 参数元组，如('%Y.%m.%d %H:%M:%S', '+1')
        """
        # 如果没有括号，返回空元组
        if '(' not in mock_params or not mock_params.endswith(')'):
            return ()

        # 提取括号内的内容
        regular = r'[\\(（].*[\\)）]$'
        match = re.search(regular, mock_params)
        if not match:
            return ()

        group = match.group(0)

        # 处理空参数情况
        if group == '()':
            return ()

        # 处理单参数情况，确保eval能正确解析
        if not group.endswith(','):
            group = f'{group[:-1]},)'

        try:
            # 安全地将字符串转换为元组
            args = eval(group)
            return args if isinstance(args, tuple) else (args,)
        except:
            return ()


# 创建全局实例
m_mock = MockM()