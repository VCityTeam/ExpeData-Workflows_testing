#!/usr/bin/env python

import codecs
import os

from setuptools import find_packages
from setuptools import setup

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

install_requires = [
    'python_version >= "3.8"',
    'kubernetes == "26.1.0"',
    "configargparse",
    'hera >= "5.6.0"',
]

version = None
exec(open("hera_utils/version.py").read())

long_description = ""
with codecs.open("./README.md", encoding="utf-8") as readme_md:
    long_description = readme_md.read()

setup(
    name="hera_utils",
    version=version,
    description="Helpers for Hera (workflows) Python framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VCityTeam/ExpeData-Workflows_testing/ArgoWorkflows/Workflows_In_Hera/hera_utils",
    project_urls={
        "Source": "https://github.com/VCityTeam/ExpeData-Workflows_testing/ArgoWorkflows/Workflows_In_Hera/hera_utils",
        "Tracker": "https://github.com/VCityTeam/ExpeData-Workflows_testing/issues",
    },
    packages=find_packages(exclude=["tests.*", "tests"]),
    python_requires=">=3.8",
    zip_safe=False,
    classifiers=[
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    maintainer="vcity_devel",
    maintainer_email="vcity@liris.cnrs.fr",
)
