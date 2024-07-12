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
import scipy
import json
import numpy as np
import pyqtgraph as pg

from PySide2 import QtWidgets

from ..options import rop
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

    # Subject
    subject_info = None

    # Screen name
    name = 'Experiment screen'

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

        # Fetch subject information
        self.subject_info = {
            'name': rop.subjectName,
            'gender': rop.subjectGender,
            'age': rop.subjectAge,
            'datetime': rop.subjectExperimentDateTime,
            'rem': rop.subjectRem
        }

        logger.info(f'Initialized with {design}')

    def _limit(self, e):
        return e

    def start(self):
        self.HID_reader.start()
        logger.debug('Started')

    def restart(self):
        self.stop()
        self.start()
        logger.debug('Restarted')

    def stop(self):
        # If the flag_stopped is set, doing nothing
        if self.flag_stopped:
            return

        # Set the flag_stopped to prevent the repeating operation
        # ! Set the flag must be very quick to truly prevent that
        self.flag_stopped = True

        # TODO: Save data
        # Get and resample all the data
        data = self.HID_reader.stop()
        # Resampling the data into 125 Hz
        data = realign_into_8ms_sampling(data)

        # Get mark
        passed = data[-1][-1]
        mark, _, _, _ = self.bm.consume(passed)
        # E refers experiment ends property
        # others refer it is stopped by force
        if mark == 'E':
            status = 'Task-finished'
        else:
            status = 'Others'

        # Subject info
        subject_info = self.subject_info

        # ----------------------------------------
        # ---- Save data and all others ----

        filename_stem = '-'.join([
            subject_info['name'],
            subject_info['datetime']])
        save_path = rop.project_root.joinpath('Data')
        paths = []
        encoding = 'gbk'

        # 1. Save data
        folder = save_path.joinpath('Data')
        path = folder.joinpath(f'{filename_stem}.json')
        path.parent.mkdir(exist_ok=True, parents=True)
        json.dump(data, open(path, 'w', encoding=encoding))
        paths.append(path)

        # 2. Save subject
        folder = save_path.joinpath('Subject')
        path = folder.joinpath(f'{filename_stem}.txt')
        path.parent.mkdir(exist_ok=True, parents=True)
        print(subject_info, file=open(path, 'w', encoding=encoding))
        paths.append(path)

        # 3. Save status
        folder = save_path.joinpath('Status')
        path = folder.joinpath(f'{filename_stem}.txt')
        path.parent.mkdir(exist_ok=True, parents=True)
        print(status, file=open(path, 'w', encoding=encoding))
        paths.append(path)

        # 4. Save experiment
        folder = save_path.joinpath('Experiment')
        path = folder.joinpath(f'{filename_stem}.txt')
        path.parent.mkdir(exist_ok=True, parents=True)
        print(self.design, file=open(path, 'w', encoding=encoding))
        paths.append(path)

        # Report
        logger.debug(f'Saved data and others into {paths}')

        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle('Saved data')
        layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QTextBrowser(parent=dialog)

        paths_string = '\n'.join([e.as_posix() for e in paths])
        content = f'''
Saved data into

{paths_string}
        '''
        message.setText(content)
        layout.addWidget(message)
        dialog.setLayout(layout)
        dialog.exec_()

        # Execute the on_stop function
        try:
            self.on_stop()
        except Exception as e:
            logger.error(f"Error executing on_stop: {e}")

        logger.debug(f'Finished: {self.design}')


def realign_into_8ms_sampling(data: list) -> np.ndarray:
    """
    Re-aligns the given data to 8 milliseconds sampling.

    Args:
        data (list): The input data to be re-aligned.

    Returns:
        np.ndarray: The re-aligned data with columns (pressure_value, digital_value, fake_pressure_value, fake_digital_value, seconds passed from the start).
    """
    # Make sure the sampling time is strictly increasing sequence
    # 1. Unique values
    m = len(data)
    d = [data[0]]
    for i in range(1, m):
        if data[i][-1] != d[-1][-1]:
            d.append(data[i])
    data = d
    m = len(data)

    # 2. Make it increasing
    data = np.array(sorted(data, key=lambda e: e[-1]))

    # ! Columns of data is
    # ! (pressure_value, digital_value, fake_pressure_value, fake_digital_value,seconds passed from the start)
    # Re-align the data to 8 milliseconds sampling
    # It equals to 125 Hz.
    max_t = data[-1, -1]
    x_realign = np.arange(0, max_t, 0.008)

    # 1. Get the sampling times
    x_sampling = data[:, 4]  # Sampling times # np.array([e[4] for e in data])

    # 2. Prepare the output data frame
    n = len(x_realign)
    realigned = np.zeros((n, 5))
    realigned[:, 4] = x_realign

    # 3. Setup the interoplate class as worker
    worker = scipy.interpolate.CubicSpline

    # 4. Interploate the other columns
    for i in range(4):
        interpolator = worker(x=x_sampling, y=data[:, i])
        realigned[:, i] = interpolator(x_realign)

    logger.debug(
        f'Realigned the data with {m} -> {n} points, interpolator is {worker}')

    return realigned.tolist()
# %% ---- 2024-07-11 ------------------------
# Play ground


# %% ---- 2024-07-11 ------------------------
# Pending


# %% ---- 2024-07-11 ------------------------
# Pending
