from setuptools import setup, find_packages

setup(
    name="staran",
    version="0.6.1",
    description="staran - 高性能Python工具库",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="StarAn",
    author_email="starlxa@icloud.com",
    license="MIT",
    url="https://github.com/starlxa/staran",
    packages=find_packages(),
    install_requires=[
        # 添加实际需要的外部依赖
        # datetime, calendar, re 都是标准库，无需列出
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
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
    keywords="machine-learning feature-engineering data-processing sql-generation",
    project_urls={
        "Bug Reports": "https://github.com/starlxa/staran/issues",
        "Source": "https://github.com/starlxa/staran",
    },
)
