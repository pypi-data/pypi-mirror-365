from setuptools import setup, find_packages

setup(
    name="llmovoice",
    version="0.0.1",
    description="Llmovoice python library",
    license="Apache License, Version 2.0",
    packages=find_packages(exclude=("tests",)),
    python_requires='>=3.10',
    include_package_data=True,
    install_requires = open('requirements.txt').readlines(),
)

