# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='moonshinewrangler',
    version='0.1.0',
    description='Python serialization library for formats used for Fender Mustang modelling guitar amplifier presets',
    long_description=readme,
    author='Tim Littlefair',
    author_email=' 5130151+tim-littlefair@users.noreply.github.com',
    url='https://github.com/tim-littlefair/moonshine-wrangler',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

