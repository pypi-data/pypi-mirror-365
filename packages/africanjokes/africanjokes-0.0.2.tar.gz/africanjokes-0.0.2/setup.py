from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='africanjokes',
    version='0.0.2', 
    description='A library for African jokes',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Morris D. Toclo',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.8',
)