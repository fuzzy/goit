#!/usr/bin/env python3

# stdlib imports
import os

# internal imports
from goit import *


config_dir = os.path.join(os.getenv("HOME"), ".config", "goit")


if __name__ == "__main__":
    app = AppSetup()
    app.run()

    app = GridApp()
    app.run()
