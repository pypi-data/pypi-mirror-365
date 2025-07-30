"""
PLTools - Python 开发工具集合

一个实用的 Python 工具包，提供常用的开发工具和实用函数。
"""

__version__ = "0.0.3"
__author__ = "PatchLion"
__email__ = "your-email@example.com"

from . import gittools

__all__ = [
    "gittools",
    "__version__",
]