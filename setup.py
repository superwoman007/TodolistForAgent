from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="todoagent",
    version="1.0.0",
    description="给 AI Agent 使用的任务管理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="superwoman007",
    url="https://github.com/superwoman007/TodolistForAgent",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "todoagent=todoagent.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
