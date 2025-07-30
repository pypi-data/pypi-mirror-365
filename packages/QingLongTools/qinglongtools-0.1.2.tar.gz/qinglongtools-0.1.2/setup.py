'''
Author: XDTEAM
Date: 2025-07-28 19:52:43
LastEditTime: 2025-07-29 21:08:30
LastEditors: XDTEAM
Description: 
'''
from setuptools import setup, find_packages

setup(
    name='QingLongTools',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'httpx',
    ],
    author='XDTEAM',
    author_email='xdteam01@163.com', # 请替换为您的邮箱
    description='A Python API wrapper for QingLong Panel',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/amumu0022/QingLongTools', # 请替换为您的项目URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # 假设使用MIT许可证
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
