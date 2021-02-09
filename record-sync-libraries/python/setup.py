#!/usr/bin/env python
# Copyright 2017 Ryan D. Williams
# Copyright 2020 Todd M. Kover
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
from setuptools import setup, find_packages

# this should be pulled in automatically
version = '0.4.0'

with open('README.txt') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

classifiers = [
    "Topic :: Utilities",
    "Programming Language :: Python",
]

setup(
    name = 'jh-recsynclib',
    version = version,
    description = 'JazzHands Record Synchronization Library',
    long_description = readme,
    author = 'Ryan D Williams',
    author_email = 'xrxdxwx@gmail.com',
    license = license,
    url = 'http://www.jazzhands.net/',
    packages = find_packages(),
    package_data = {'jh_recsynclib': ['json_schema/*.json']},
    classifiers = classifiers
)
