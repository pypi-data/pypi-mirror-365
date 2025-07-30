from setuptools import setup, find_packages

setup(
    name="staran",
    version="1.0.11",
    description="staran - 企业级Python日期处理库",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="StarAn",
    author_email="starlxa@icloud.com",
    license="MIT",
    url="https://github.com/starlxa/staran",
    packages=find_packages(),
    install_requires=[
        # 核心功能零外部依赖
    ],
    extras_require={
        # v1.0.10 扩展功能的可选依赖
        'visualization': [
            'matplotlib>=3.0.0',
            'plotly>=5.0.0',
        ],
        'web': [
            'flask>=2.0.0',  # API服务器可选依赖
        ],
        'full': [
            # 安装所有可选依赖
            'matplotlib>=3.0.0',
            'plotly>=5.0.0', 
            'flask>=2.0.0',
        ],
        'dev': [
            # 开发依赖
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
            'mypy>=0.800',
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Software Development :: Localization",
        "Topic :: Scientific/Engineering :: Visualization",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    keywords="date datetime utilities time-processing lunar calendar i18n timezone visualization api",
    project_urls={
        "Bug Reports": "https://github.com/starlxa/staran/issues",
        "Source": "https://github.com/starlxa/staran",
        "Documentation": "https://github.com/starlxa/staran/blob/master/API_REFERENCE.md",
    },
    entry_points={
        'console_scripts': [
            'staran=staran.date.utils.cli:main',  # 命令行工具 (如果需要)
        ],
    },
)
