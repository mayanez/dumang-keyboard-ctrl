import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name="dumang_ctrl",
    version="0.0.2",
    description="Dumang DK6 Tools",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/mayanez/",
    author="Miguel A. Arroyo",
    author_email="dumang@arroyo.me",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["docopt", "pyudev", "hidapi", "PyQt5"],
    entry_points={
        "console_scripts": [
            "dumang-sync = dumang_ctrl.tools.sync:main",
            "dumang-config = dumang_ctrl.tools.config:main"
        ]
    },
)
