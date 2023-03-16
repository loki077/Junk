import os, sys, re

from helloworld import __version__ as version

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()

SETUP_ARGS = dict(
    name='helloworld',
    version=version,
    description=('Grabs the "Hello World" Wikipedia page and prints its title'),
    long_description=long_description,
    url='https://github.com/<your login>/helloworld',
    author='<AUTHOR>',
    author_email='<EMAIL>',
    license='MIT',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    py_modules = ['helloworld',],
    install_requires = [
        'requests>=2.22',
    ],
)

if __name__ == '__main__':
    from setuptools import setup, find_packages

    SETUP_ARGS['packages'] = find_packages()
    setup(**SETUP_ARGS)
