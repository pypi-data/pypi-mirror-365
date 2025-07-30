# AI Tools

一个简单的Python工具包，提供基础的AI相关工具函数。

## 安装

```bash
pip install lchpersonal-ai-tools
```

## 使用方法

```python
from ai_tools import sayHello, add_numbers, greet_user, get_current_time

# 基础问候
sayHello()  # 输出: hello world!

# 数学运算
add_numbers(10, 20)  # 输出: 10 + 20 = 30

# 自定义问候
greet_user("张三")  # 输出: Hello, 张三!

# 工具函数
print(get_current_time())  # 输出当前时间
```

## 功能

- `sayHello()`: 输出 "hello world!" 消息
- `sayGoodbye()`: 输出 "goodbye world!" 消息
- `add_numbers(a, b)`: 两个数字相加
- `greet_user(name)`: 向指定用户问好
- `get_current_time()`: 获取当前时间
- `get_random_number(min_val, max_val)`: 获取指定范围内的随机数
- `reverse_string(text)`: 反转字符串

## 要求

- Python 3.7+

## 许可证

MIT License

## 开发

### 本地安装开发版本

```bash
git clone https://github.com/lchpersonal/ai-tools.git
cd ai-tools
pip install -e .
```

### 运行测试

```bash
python -m pytest tests/
```

### 构建包

```bash
python -m build
```

## 更新日志

### 0.1.0
- 初始版本
- 添加sayHello函数 