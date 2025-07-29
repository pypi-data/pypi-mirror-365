from setuptools import setup, find_packages

from df_types._version import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="df-types",
    version=__version__,
    packages=find_packages(),
    description="A tool for generating dataclass type files for pandas DataFrame rows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="jon-edward",
    license="MIT",
    url="https://github.com/jon-edward/df-types",
    keywords=["python", "pandas", "dataclass", "dataframe"],
    requires=["pandas"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
)