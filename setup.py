from setuptools import setup, find_packages

setup(
    name="hpi",
    version="5.0.2",
    packages=find_packages(),
    install_requires=[
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "matplotlib>=3.8.2",
        "numpy>=1.26.3"
    ]
) 