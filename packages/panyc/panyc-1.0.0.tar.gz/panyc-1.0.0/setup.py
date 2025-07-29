from setuptools import find_packages, setup

with open("README.md", "r") as f:
	description = f.read()

setup(
    name='panyc',
    version='1.0.0',
    description='',
    long_description=description,
    long_description_content_type="text/markdown",
    author='bnz',
    author_email='matteo.benzi97@gmail.com',
    url='https://codeberg.org/bnz/panyc',
    license="MIT",
    scripts=["panyc.py"],
)
