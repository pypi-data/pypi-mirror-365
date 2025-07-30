"""
AI Tools 工具函数模块
"""

import random
from datetime import datetime


def get_random_number(min_val=1, max_val=100):
    """
    获取随机数
    
    Args:
        min_val (int): 最小值
        max_val (int): 最大值
    
    Returns:
        int: 随机数
    """
    return random.randint(min_val, max_val)


def get_current_time():
    """
    获取当前时间
    
    Returns:
        str: 格式化的当前时间
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def reverse_string(text):
    """
    反转字符串
    
    Args:
        text (str): 要反转的字符串
    
    Returns:
        str: 反转后的字符串
    """
    return text[::-1] 