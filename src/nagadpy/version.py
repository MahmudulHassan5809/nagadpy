import os

__version__ = "0.0.3"

if os.environ.get("ENV") == "test":
    __version__ += "-test"
