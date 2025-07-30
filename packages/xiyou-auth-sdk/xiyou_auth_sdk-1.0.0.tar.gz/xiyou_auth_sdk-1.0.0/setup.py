"""
Xiyou OpenAPI Python SDK 安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xiyou-auth-sdk",
    version="1.0.0",
    author="Xiyou SDK Team",
    author_email="support@xiyou.com",
    description="Xiyou OpenAPI Python认证SDK - 提供完整的加签认证功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiyou/xiyou-python-auth-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.7",
    install_requires=[
        # 无需外部依赖，只使用Python标准库
    ],
    keywords="xiyou api auth signature hmac authentication",
    project_urls={
        "Bug Reports": "https://github.com/xiyou/xiyou-python-auth-sdk/issues",
        "Source": "https://github.com/xiyou/xiyou-python-auth-sdk",
        "Documentation": "https://docs.xiyou.com",
    },
)
