from setuptools import setup, find_packages

setup(
    name='staran',
    version='0.1.0',
    description='A short description of your package',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='StarAn',
    author_email='starlxa@icloud.com',
    url='https://github.com/starlxa/staran',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.20',
        'pandas'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)