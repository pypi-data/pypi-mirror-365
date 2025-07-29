# m-mock - 智能模拟数据生成库


m-mock是一个功能强大的Python模拟数据生成库，支持生成各种类型的随机数据，包括日期时间、数字、字符串、姓名、文本等。

## 功能特点

- 📅 **日期时间**：生成随机日期、时间、时间戳
- 🔢 **数字类型**：整数、浮点数、自然数
- 🔤 **文本类型**：中英文句子、段落、混合文本
- 👤 **姓名生成**：中英文姓名、姓氏、名字
- 🆔 **标识符**：UUID、自增ID、中国身份证号
- 🎲 **随机选择**：从列表中随机选取元素
- 🛠️ **易于扩展**：支持自定义数据生成规则

## 安装

```bash
pip install m-mock
```

## 快速开始

### 基本使用

```python
from m-mock import m_mock

# 生成随机日期
print(m_mock.mock("@date()"))  # 输出: "2023-07-15"

# 生成随机中文姓名
print(m_mock.mock("@cname()"))  # 输出: "张三"

# 生成随机浮点数
print(m_mock.mock("@float(1,100)"))  # 输出: 56.78
```

### 高级用法

```python
# 带参数的日期生成
print(m_mock.mock("@date('%Y年%m月%d日','+3d')"))  # 输出: "2023年07月18日"

# 生成随机段落
print(m_mock.mock("@cparagraph(5,8)"))  # 输出: "这是一个随机生成的中文段落..."

# 从列表中选择
print(m_mock.mock("@pick(['苹果','香蕉','橙子'])"))  # 输出: "香蕉"
```

## 完整API参考

### 日期时间

| 表达式                    | 描述         | 示例                      |
| ------------------------- | ------------ | ------------------------- |
| `@date()`                 | 当前日期     | "2023-07-15"              |
| `@date(format, interval)` | 格式化日期   | `@date('%Y/%m/%d','+1d')` |
| `@datetime()`             | 当前日期时间 | "2023-07-15 14:30:00"     |
| `@time()`                 | 当前时间     | "14:30:00"                |
| `@timestamp()`            | 时间戳(毫秒) | 1689409800000             |
| `@now(unit)`              | 指定单位时间 | `@now('month')`           |

### 数字类型

| 表达式                        | 描述       | 示例                     |
| ----------------------------- | ---------- | ------------------------ |
| `@integer(min,max)`           | 随机整数   | `@integer(1,100)` → 42   |
| `@float(min,max,d_min,d_max)` | 随机浮点数 | `@float(0,1,2,4)` → 0.75 |
| `@natural(min,max)`           | 自然数     | `@natural(10,20)` → 15   |
| `@boolean()`                  | 布尔值     | True/False               |

### 文本相关

| 表达式                   | 描述       | 示例                                      |
| ------------------------ | ---------- | ----------------------------------------- |
| `@string(type,min,max)`  | 随机字符串 | `@string('lower',5,10)` → "abcdef"        |
| `@character(type)`       | 随机字符   | `@character('upper')` → "A"               |
| `@sentence(min,max)`     | 英文句子   | `@sentence(5,10)` → "This is a sentence." |
| `@csentence(min,max)`    | 中文句子   | `@csentence(5,10)` → "这是一个句子。"     |
| `@paragraph(min,max)`    | 英文段落   | `@paragraph(3,5)` → "A paragraph..."      |
| `@cparagraph(min,max)`   | 中文段落   | `@cparagraph(3,5)` → "这是一个段落..."    |
| `@mix_sentence(min,max)` | 混合文本   | `@mix_sentence(5,10)` → "Hello 世界 123"  |

### 姓名相关

| 表达式            | 描述     | 示例                  |
| ----------------- | -------- | --------------------- |
| `@name()`         | 英文姓名 | "John Smith"          |
| `@cname()`        | 中文姓名 | "张三"                |
| `@first()`        | 英文姓氏 | "Smith"               |
| `@last()`         | 英文名字 | "John"                |
| `@clast()`        | 中文姓氏 | "张"                  |
| `@cfirst(length)` | 中文名字 | `@cfirst(2)` → "三丰" |

### 其他功能

| 表达式             | 描述         | 示例                               |
| ------------------ | ------------ | ---------------------------------- |
| `@pick(list)`      | 从列表选择   | `@pick(['A','B','C'])` → "B"       |
| `@increment(step)` | 自增数字     | `@increment(2)` → "2", "4", "6"... |
| `@uuid()`          | UUID生成     | "a1b2c3d4..."                      |
| `@id()`            | 中国身份证号 | "110105199003072316"               |

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork仓库
2. 创建特性分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT License 许可证。