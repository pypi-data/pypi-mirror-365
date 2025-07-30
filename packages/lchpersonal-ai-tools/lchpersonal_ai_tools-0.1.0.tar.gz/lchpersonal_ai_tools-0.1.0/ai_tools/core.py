"""
AI Tools 核心功能模块
"""


def sayHello():
    """
    输出hello world!
    
    Returns:
        str: 返回hello world!字符串
    """
    message = "hello world!"
    print(message)
    return message


def sayGoodbye():
    """
    输出goodbye world!
    
    Returns:
        str: 返回goodbye world!字符串
    """
    message = "goodbye world!"
    print(message)
    return message


def add_numbers(a, b):
    """
    两个数字相加
    
    Args:
        a (int): 第一个数字
        b (int): 第二个数字
    
    Returns:
        int: 两数之和
    """
    result = a + b
    print(f"{a} + {b} = {result}")
    return result


def greet_user(name="World"):
    """
    向用户问好
    
    Args:
        name (str): 用户名称，默认为"World"
    
    Returns:
        str: 问候消息
    """
    message = f"Hello, {name}!"
    print(message)
    return message 