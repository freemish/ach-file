from distutils.core import setup
from setuptools import find_packages

setup(
    name='ach-file',
    author='Molly Gouletas',
    author_email='molly.gouletas@gmail.com',
    version='0.1.6.beta',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/freemish/ach-file',
    license='MIT License',
    description='Highly configurable and permissive library to generate ACH files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
