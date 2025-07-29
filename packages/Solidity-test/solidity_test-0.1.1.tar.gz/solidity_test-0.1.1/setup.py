from setuptools import setup, find_packages

setup(
    name="Solidity_test",
    version="0.1.1",
    description="Octobizteam IT Developer Technical Test",
    author="masbro",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
    ],
    python_requires=">=3.6",
)