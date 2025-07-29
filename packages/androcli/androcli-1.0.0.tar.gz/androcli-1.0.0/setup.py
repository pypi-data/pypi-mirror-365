#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='androcli',
    version='1.0.0',
    author='AryanVBW',
    author_email='whitedevil367467@gmail.com',
    description='Android CLI tool for reverse shell operations and APK building',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AryanVBW/androcli',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development',
        'Topic :: System :: Networking',
        'Topic :: Security',
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'androcli=androcli.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'androcli': [
            'Jar_utils/*.jar',
            'Compiled_apk/**/*',
            'Android_Code/**/*',
        ],
    },
    keywords='android, reverse-shell, apk, cli, security, penetration-testing',
    project_urls={
        'Bug Reports': 'https://github.com/AryanVBW/androcli/issues',
        'Source': 'https://github.com/AryanVBW/androcli',
    },
)