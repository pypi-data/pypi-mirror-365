from m_mock.mock import m_mock


def execute_mock(params):
    result = m_mock.mock(params)
    print(f"m_mock.mock('{params}'):{result}")
