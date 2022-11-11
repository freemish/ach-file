from distutils.core import setup

setup(
    name='ach-file',
    author='Molly Gouletas',
    author_email='molly.gouletas@gmail.com',
    version='0.1.0',
    packages=[
        'ach',
    ],
    url='https://github.com/freemish/ach-file',
    license='MIT License',
    description='Highly configurable and permissive library to generate ACH files',
    long_description=open('README.md').read(),
)