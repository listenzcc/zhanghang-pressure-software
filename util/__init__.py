"""
File: __init__.py
Author: Chuncheng Zhang
Date: 2024-07-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Initialize the project of zhanghang pressure software

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-09 ------------------------
# Requirements and constants
import sys

from pathlib import Path
from loguru import logger


# %% ---- 2024-07-09 ------------------------
# Function and class
def get_project_root():
    return Path(sys.argv[0]).parent


def setup_logger(path: Path):
    logger.add(path, rotation='5 MB')


# %% ---- 2024-07-09 ------------------------
# Play ground
project_name = 'Pressure Software HangZhang v1.0'
software_version = 1.0

project_root = get_project_root()
setup_logger(project_root.joinpath(f'log/{project_name}.log'))


# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
