import os
from pathlib import Path
import sys
# insert root path
sys.path.insert(1, os.path.join(Path(__file__).resolve().parent.parent))

import json

with open(os.path.join(Path(__file__).resolve().parent.parent, 'res', 'settings.json'), 'r') as f:
    SETTINGS = json.load(f)

vs = "1.0.0"

class PATH:
    home = os.path.expanduser("~")
    root = Path(__file__).resolve().parent.parent
    if os.path.exists(os.path.join(home, 'Downloads')):
        download = os.path.join(home, 'Downloads')
    elif os.path.exists(os.path.join(home, 'downloads')):
        download = os.path.join(home, 'downloads')
    else:
        download = os.path.join(root, 'downloads')

