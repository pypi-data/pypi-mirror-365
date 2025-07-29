from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='simple-orm-sqlite',
    version='0.0.1',
    license='MIT License',
    author='Danilo Souza',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='danilocrautomacao@gmail.com',
    keywords='sqlite orm',
    description=u'Basic Orm for sqlite',
    packages=['simple_orm'],
    install_requires=[],)