# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# 读取 README 文件（如果有的话）
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Private API for abu"

setup(
    name='py-abu',  # PyPI 上的名称可以保留连字符
    version='1.3.4',
    description='abu API',
    long_description=long_description,
    long_description_content_type="text/markdown",  # 添加这一行
    author='Chris',
    author_email='10512@qq.com',
    url='https://github.com/ChrisYP/abu',
    license='MIT',
    packages=find_packages(),
    # 删除 package_dir 这一行，因为可能导致问题
    # package_dir={'py-abu': 'abu'},
    install_requires=[
        "loguru",
        "pyperclip",
        "requests",
        "aiohttp",
        "Brotli",
        "msoffcrypto-tool",
        "pandas",
        "openpyxl"
    ],
    platforms=["all"],
    include_package_data=True,
    zip_safe=False,
    keywords='abu',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.6',  # 添加 Python 版本要求
)
