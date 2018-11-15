# pylint: disable=missing-docstring
import setuptools
from confjson import __version__

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="confjson",
    version=__version__,
    author="Namida Aneskans",
    author_email="namida@skunkfrukt.se",
    description="A bafflingly simple, JSON-backed user configuration manager.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/skunkfrukt/confjson",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
)
