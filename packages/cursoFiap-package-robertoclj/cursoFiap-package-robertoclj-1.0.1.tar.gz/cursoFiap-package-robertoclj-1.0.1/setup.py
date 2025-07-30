from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='cursoFiap-package-robertoclj',
    version='1.0.1',
    packages=find_packages(),
    description='Descricao da sua lib cursoFiap',
    author='Roberto Costa Lima Jr',
    author_email='robertoclj@gmail.com',
    url='https://github.com/robertoclj/cursoFiap',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
