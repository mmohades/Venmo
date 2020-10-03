#!/usr/bin/env python

"""The setup script."""
from setuptools import setup, find_packages

with open('README.md', encoding = "utf-8") as readme_file:
    readme = readme_file.read()


def requirements():
    """Build the requirements list for this project"""
    requirements_list = []

    with open('requirements.txt',  encoding = "utf-8") as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list


requirements = requirements()

setup(
    name='venmo-api',
    version='0.2.2',
    author="Mark Mohades",
    license="GNU General Public License v3",
    url='https://github.com/mmohades/venmo',
    keywords='Python Venmo API wrapper',
    description="A Simple Python Wrapper For The Venmo API",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.6',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
