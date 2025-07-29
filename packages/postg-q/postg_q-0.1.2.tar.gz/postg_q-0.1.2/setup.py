from setuptools import setup, find_packages

setup(
    name='postg-q',  # твое уникальное имя на PyPI
    version='0.1.2',
    description='Minimal PostgreSQL utility with psycopg2',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='bigint001 (Ivan Pohorilyi)',
    author_email='thepatrickmaps@gmail.com',
    url='https://github.com/bigint001/postg',
    packages=find_packages(),  # вместо py_modules — находит папки с __init__.py
    install_requires=[
        'psycopg2-binary',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
