"""
AI Tools - 一个简单的Python工具包
"""

from .core import sayHello, sayGoodbye, add_numbers, greet_user
from .utils import get_random_number, get_current_time, reverse_string

__version__ = "0.1.0"
__author__ = "lchpersonal"
__email__ = "326018662@qq.com"

# 导出主要函数
__all__ = [
    "sayHello", 
    "sayGoodbye", 
    "add_numbers", 
    "greet_user",
    "get_random_number",
    "get_current_time", 
    "reverse_string"
] 