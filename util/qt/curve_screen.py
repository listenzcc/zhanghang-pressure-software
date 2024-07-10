"""
File: curve_screen.py
Author: Chuncheng Zhang
Date: 2024-07-10
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Amazing things

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-10 ------------------------
# Requirements and constants
import numpy as np
import pyqtgraph as pg

from PySide2.QtGui import QFont

from ..device.realtime_hid_reader import RealTimeHIDReader
from ..options import rop
from .. import logger


# %% ---- 2024-07-10 ------------------------
# Function and class

class CurveScreen(pg.PlotWidget):
    # Basic setup
    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")
    pg.setConfigOption("antialias", True)

    # Curves
    feedback_pen = pg.mkPen(color='red')
    reference_pen = pg.mkPen(color='green')
    delayed_pen = pg.mkPen(color='blue')

    feedback_curve = None
    reference_curve = None
    delayed_curve = None

    # HID reader
    HID_reader = None

    # Experiment
    design = None
    led_y = None
    led_t = None

    def __init__(self, design, led_y, led_t):
        self.HID_reader = RealTimeHIDReader()
        self.design = design
        self.led_y = led_y
        self.led_t = led_t
        super().__init__()
        self._put_components()
        logger.info(f'Initialized with {design}')

    def _put_components(self):
        self.feedback_curve = self.plot([], [], pen=self.feedback_pen)
        self.reference_curve = self.plot([], [], pen=self.reference_pen)
        self.delayed_curve = self.plot([], [], pen=self.delayed_pen)

    def _limit(self, e):
        return e

    def draw(self):
        # Compute peek_length based on delayedLength option
        peek_length = np.max([10, rop.delayedLength*2])

        # Get data
        data = self.HID_reader.peek_by_seconds(peek_length, peek_delay=False)
        data = np.array(data)

        # Set data
        real_y = data[:, 0]
        fake_y = data[:, 2]
        times = data[:, 4]
        ref_y = np.zeros(times.shape) + rop.yReference
        self.feedback_curve.setData(times, self._limit(real_y))
        self.reference_curve.setData(times, self._limit(ref_y))

        # Get delayed_data
        delayed_data = self.HID_reader.peek_by_seconds(
            peek_length, peek_delay=True)
        delayed_data = np.array(delayed_data)

        # Set delayed data
        if len(delayed_data) > 0:
            real_d_y = delayed_data[:, 0]
            fake_d_y = delayed_data[:, 1]
            d_times = delayed_data[:, 4]
            self.delayed_curve.setData(d_times, self._limit(real_d_y))

        # Set Pen
        self.reference_pen.setColor(rop.referenceCurveColor)
        self.reference_pen.setWidth(rop.referenceCurveWidth)
        self.feedback_pen.setColor(rop.feedbackCurveColor)
        self.feedback_pen.setWidth(rop.feedbackCurveWidth)
        self.delayed_pen.setColor(rop.delayedCurveColor)
        self.delayed_pen.setWidth(rop.delayedCurveWidth)

        # Set range
        self.setYRange(rop.yMin, rop.yMax)
        # Keep the current data point on the horizontal center
        self.setXRange(times[0], 2*times[-1] - times[0])

        # Set LED
        self.led_y.display(f'{real_y[-1]:0.2f}')
        self.led_t.display(f'{times[-1]:0.2f}')

    def start(self):
        self.HID_reader.start()
        logger.debug('Start')

    def stop(self):
        self.HID_reader.stop()
        logger.debug('Stop')

    def restart(self):
        self.stop()
        self.start()
        logger.debug('Restart')


# %% ---- 2024-07-10 ------------------------
# Play ground


# %% ---- 2024-07-10 ------------------------
# Pending


# %% ---- 2024-07-10 ------------------------
# Pending
