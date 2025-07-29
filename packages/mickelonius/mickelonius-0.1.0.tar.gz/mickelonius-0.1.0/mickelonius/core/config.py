import os
import pathlib

from pydantic import BaseSettings


MICKELONIUS_PKG_DIR = pathlib.Path(__file__).parent.absolute() # /data1/repos/mickelonius/mickelonius
MICKELONIUS_DIR = pathlib.Path(__file__).parent.parent.absolute() # /data1/repos/mickelonius
MICKELONIUS_TEST_DATA_DIR = os.environ.get("MICKELONIUS_TEST_DATA_DIR", MICKELONIUS_DIR / "test/data")
MICKELONIUS_DATA_DIR = os.environ.get("MICKELONIUS_DATA_DIR", MICKELONIUS_DIR / "data")

class EnvSettings(BaseSettings):
    host: str = "localhost"
    port: int = 8000

    class Config:
        env_prefix = "MICKELONIUS_"  # environment variables like MICKELONIUS_HOST

env_settings = EnvSettings()
