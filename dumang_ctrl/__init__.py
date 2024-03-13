name = "dumang_ctrl"
version_info = (1, 0, 0)
version = '.'.join(str(c) for c in version_info)
description = "Dumang DK6 Tools"
url = "https://github.com/mayanez/dumang-keyboard-ctrl"

import logging
import sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
