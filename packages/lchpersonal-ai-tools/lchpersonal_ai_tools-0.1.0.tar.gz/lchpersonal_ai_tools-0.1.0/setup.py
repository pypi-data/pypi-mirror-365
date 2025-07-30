"""
Setup script for lchpersonal package
"""

from setuptools import setup, find_packages

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="lchpersonal-ai-tools",
    version="0.1.0",
    author="lchpersonal",
    author_email="326018662@qq.com",
    description="简单实用的AI工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lchpersonal/ai-tools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="ai tools utilities",
    project_urls={
        "Bug Reports": "https://github.com/lchpersonal/ai-tools/issues",
        "Source": "https://github.com/lchpersonal/ai-tools",
    },
) 