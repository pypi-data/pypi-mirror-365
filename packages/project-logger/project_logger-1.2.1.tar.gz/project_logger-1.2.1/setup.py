from setuptools import setup, find_packages
import os

setup(
    name="project_logger",
    version="1.2.1",
    packages=find_packages(),
    package_data={
        'project_logger': ['*.py', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.env'],
        'project_logger.pyarmor_runtime_000000': ['*.pyd', '*.py', '*.so', '*.dll'],
    },
    include_package_data=True,
    install_requires=[
        "pymysql",
        "dbutils",
    ],
    author="Funnel",
    author_email="sunn61676@gmail.com",
    description="A security logging package for Python projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    zip_safe=False,  # 加密包不能使用zip安装
)