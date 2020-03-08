import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="dumang_ctrl",
    version="0.0.1",
    description="Dumang DK6 Tools",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/mayanez/",
    author="Miguel A. Arroyo",
    author_email="email@arroyo.me",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["dumang_ctrl", "dumang_ctrl.dumang"],
    include_package_data=True,
    install_requires=["docopt", "pyudev", "hidapi", "PyQt5"],
    entry_points={
        "console_scripts": [
            "dumang-sync = dumang_ctrl.tools.sync:main",
            "dumang-config = dumang_ctrl.tools.config:main"
        ]
    },
)
