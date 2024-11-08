#!/usr/bin/env python3

# stdlib imports
import os

# internal imports
from goitlib import *

# Global settings for cache
config_dir = os.path.join(os.getenv("HOME"), ".config", "goit")


def main():
    app = AppSetup()
    app.run()

    app = GridApp()
    app.run()


if __name__ == "__main__":
    main()
