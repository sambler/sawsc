#!/usr/bin/env python
# -*- coding: utf-8 -*-

# my default setup.py
# adjusted from https://github.com/kennethreitz/setup.py

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys

from setuptools import find_packages, setup, Command
#from Cython.Build import cythonize

# Package meta-data.
NAME = 'sawsc'
DESCRIPTION = "Shane's AWS Configurator."
URL = 'https://github.com/sambler/sawsc'
EMAIL = 'develop@shaneware.biz'
AUTHOR = 'Shane Ambler'
REQUIRES_PYTHON = '>=3.8.0'
VERSION = '1.0.2'

# What packages are required for this module to be executed?
REQUIRED = [
    'boto3',
    'tkinter',
    'ttkbootstrap',
]

# packages used during tests
TEST_EXTRAS = [
    #'pytest',
    #'pytest-cov',
    #'coverage',
    #'tox',
    #'codetiming',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

EXT_MODULES = [] #cythonize('module/*.py')

ENTRY_POINTS = {
    'console_scripts': ['sawscui = sawsc.gui:main',
                        'sawsc = sawsc.cmd:main',],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
command = sys.argv[-1]
long_description = ''
if command not in ['test', 'coverage']:
    try:
        with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
            long_description = '\n' + f.read()
    except FileNotFoundError:
        long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    # for a project of multiple packages use:
    # packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    py_modules=[NAME],
    ext_modules=EXT_MODULES,
    entry_points=ENTRY_POINTS,
    install_requires=REQUIRED,
    tests_require=TEST_EXTRAS,
    extras_require=EXTRAS,
    include_package_data=True,
    zip_safe=True,
    license='bsd',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
