from setuptools import setup, find_packages

setup(
    name="staran",
    version="1.0.0",
    description="staran - 轻量级Python日期工具库",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="StarAn",
    author_email="starlxa@icloud.com",
    license="MIT",
    url="https://github.com/starlxa/staran",
    packages=find_packages(),
    install_requires=[
        # 只使用Python标准库，无外部依赖
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="date datetime utilities time-processing",
    project_urls={
        "Bug Reports": "https://github.com/starlxa/staran/issues",
        "Source": "https://github.com/starlxa/staran",
    },
)
