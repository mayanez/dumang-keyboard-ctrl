import importlib.metadata
import logging
import sys

pkgmetadata = importlib.metadata.metadata(__package__)
version = pkgmetadata['Version']
description = pkgmetadata['Summary']
url = pkgmetadata['Home-page']

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
