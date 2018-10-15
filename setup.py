import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="confjson",
    version="1.1.0",
    author="Namida Aneskans",
    author_email="namida@skunkfrukt.se",
    description="A bafflingly simple, JSON-backed user configuration manager.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skunkfrukt/confjson",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
)
