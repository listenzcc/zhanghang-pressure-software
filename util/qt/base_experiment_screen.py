"""
File: base_experiment_screen.py
Author: Chuncheng Zhang
Date: 2024-07-11
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Base class for the experiment screen

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-11 ------------------------
# Requirements and constants
import pyqtgraph as pg
from PySide2 import QtCore

from ..block_manager import BlockManager
from ..device.realtime_hid_reader import RealTimeHIDReader

from .. import logger


# %% ---- 2024-07-11 ------------------------
# Function and class


class BaseExperimentScreen(pg.PlotWidget):
    '''
    A pg.PlotWidget instance.

    Provide basic functionality for the experiment screen

    - components:
        - HID_reader: RealTimeHIDReader
        - lcd numbers
        - progress_bar
        - design: dict
        - bm: BlockManager
        - frames: int

    - functions:
        - _limit
        - start
        - stop
        - restart
    '''

    # Basic setup
    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")
    pg.setConfigOption("antialias", True)

    # HID reader
    HID_reader: RealTimeHIDReader = None  # RealTimeHIDReader for pressure value

    # Experiment
    design: dict = None  # Must be a legal block design
    bm: BlockManager = None  # Instance of BlockManager of design
    lcd_y = None  # lcd Number widget for pressure
    lcd_t = None  # lcd Number widget for times
    progress_bar = None  # Progress bar
    frames: int = 0  # How many frames were displayed

    # OnStop function
    on_stop = None
    flag_stopped = False

    def __init__(self, design: dict, lcd_y, lcd_t, progress_bar, on_stop):
        # Initialize super
        super().__init__()

        # Initialize device
        self.HID_reader = RealTimeHIDReader()
        self.design = design
        self.bm = BlockManager(design)

        # Initialize the lcd numbers
        self.lcd_y = lcd_y
        self.lcd_t = lcd_t
        self.progress_bar = progress_bar

        # Bind the on_top function
        self.on_stop = on_stop

        logger.info(f'Initialized with {design}')

    def _limit(self, e):
        return e

    def start(self):
        self.HID_reader.start()
        logger.debug('Started')

    def stop(self):
        self.HID_reader.stop()
        logger.debug('Stopped')

    def restart(self):
        self.stop()
        self.start()
        logger.debug('Restarted')

# %% ---- 2024-07-11 ------------------------
# Play ground


# %% ---- 2024-07-11 ------------------------
# Pending


# %% ---- 2024-07-11 ------------------------
# Pending
