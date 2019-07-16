# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tclwrapper',
    version='0.0.1',
    description='Python wrapper for programs that expose a tcl interface',
    long_description=long_description,
    url='https://github.com/csail-csg/tclwrapper',
    author='CSAIL CSG',
    author_email='acwright@mit.edu',
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Tcl',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='TCL Wrapper tclsh wish',
    packages=find_packages(exclude=[]),
    include_package_data=True,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        # If we ever want to add an executable script, this is where it goes
    },
    project_urls={
        'Bug Reports': 'https://github.com/csail-csg/tclwrapper/issues',
        'Source': 'https://github.com/csail-csg/tclwrapper',
    },
)
