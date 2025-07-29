from setuptools import setup, find_packages

setup(
    name="myutilslitdddddd",  # 包名（pip install 后的名称）
    version="0.1.1",  # 版本号（遵循语义化版本）
    author="Your Name",
    author_email="your@email.com",
    description="一个自定义工具函数bao 哈哈哈",  # 简短描述

    url="https://github.com/yourname/myutils",  # 项目地址（可选）
    packages=find_packages(),  # 自动发现包目录
    classifiers=[  # 分类信息（可选，用于PyPI搜索）
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",  # 支持的Python版本
    # install_requires=["requests"],  # 依赖的其他库（可选）
)