from setuptools import setup

setup(
    name='postg-q',
    version='0.1.0',
    description='Minimal PostgreSQL utility with psycopg2',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='bigint001 (Ivan Pohorilyi)',
    author_email='thepatrickmaps@gmail.com',
    url='https://github.com/bigint001/postg',
    py_modules=['postg'],
    install_requires=[
        'psycopg2-binary',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)