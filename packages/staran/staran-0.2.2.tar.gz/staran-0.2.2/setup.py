from setuptools import setup, find_packages

setup(
    name='staran',
    version='0.2.2',
    description='staran - 高性能Python工具库',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='StarAn',
    author_email='starlxa@icloud.com',
    url='https://github.com/starlxa/staran',
    packages=['staran', 'staran.tools'],
    install_requires=[
        'datetime',
        'calendar',
        're',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)