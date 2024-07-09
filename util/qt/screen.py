"""
File: screen.py
Author: Chuncheng Zhang
Date: 2024-07-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Main screen

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-09 ------------------------
# Requirements and constants
import numpy as np
import pyqtgraph as pg

from PIL import Image

from .. import logger


# %% ---- 2024-07-09 ------------------------
# Function and class
class MainScreen(pg.PlotWidget):
    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")
    pg.setConfigOption("antialias", True)

    def __init__(self):
        super().__init__()
        logger.info('Initialized')


# %% ---- 2024-07-09 ------------------------
# Play ground


# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
