"""
测试ai_tools.core模块
"""

import pytest
from io import StringIO
import sys
from ai_tools.core import sayHello, sayGoodbye, add_numbers, greet_user


def test_sayHello():
    """测试sayHello函数"""
    # 捕获print输出
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # 调用函数
    result = sayHello()
    
    # 恢复stdout
    sys.stdout = sys.__stdout__
    
    # 验证返回值
    assert result == "hello world!"
    
    # 验证print输出
    assert captured_output.getvalue().strip() == "hello world!"


def test_sayGoodbye():
    """测试sayGoodbye函数"""
    captured_output = StringIO()
    sys.stdout = captured_output
    
    result = sayGoodbye()
    
    sys.stdout = sys.__stdout__
    
    assert result == "goodbye world!"
    assert captured_output.getvalue().strip() == "goodbye world!"


def test_add_numbers():
    """测试add_numbers函数"""
    result = add_numbers(3, 5)
    assert result == 8
    
    result = add_numbers(0, 0)
    assert result == 0
    
    result = add_numbers(-1, 1)
    assert result == 0


def test_greet_user():
    """测试greet_user函数"""
    # 测试默认参数
    result = greet_user()
    assert result == "Hello, World!"
    
    # 测试自定义名称
    result = greet_user("Alice")
    assert result == "Hello, Alice!"


def test_sayHello_return_type():
    """测试sayHello函数返回类型"""
    result = sayHello()
    assert isinstance(result, str)


def test_sayHello_multiple_calls():
    """测试多次调用sayHello函数"""
    for _ in range(3):
        result = sayHello()
        assert result == "hello world!" 