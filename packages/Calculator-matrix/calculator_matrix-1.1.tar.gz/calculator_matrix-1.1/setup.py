import setuptools
from pathlib import Path

setuptools.setup(
    name="Calculator_matrix",
    version=1.1,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["Data", "tests"]),
    install_requires=["numpy"],
)


setup(
    ...,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
