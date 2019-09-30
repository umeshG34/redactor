from setuptools import setup, find_packages

setup(
    name='redactor',
    version='1.0',
    author='Umesh Sai Gurram',
    authour_email='umXsXsXiXX@XX.com',
    packages=find_packages(exclude=('tests', 'docs')),
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
    )
