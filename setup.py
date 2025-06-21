from setuptools import find_packages, setup

setup(
    name="hpi",
    version="0.6.2",
    packages=find_packages(),
    install_requires=[
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "matplotlib>=3.8.2",
        "numpy>=1.26.3",
    ],
    python_requires=">=3.8",
    author="Ya88",
    description="Human Performance Index - Track and analyze life metrics",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
