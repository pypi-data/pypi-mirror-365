from __future__ import annotations

import os
import sys
from pathlib import Path

if _value := os.environ.get('SWENV_DATA_DIR'):
    DATA_DIR = Path(_value)
else:
    DATA_DIR = Path(os.environ.get('APPDATA', '~\\AppData\\Roaming' if sys.platform == 'win32' else '~/.local/share')).expanduser().joinpath('swenv')

DEFAULT_CONFIG_URL = os.environ.get('SWENV_DEFAULT_CONFIG_URL', 'http://{nexus}/swenv-config.zip')
