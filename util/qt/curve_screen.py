"""
File: curve_screen.py
Author: Chuncheng Zhang
Date: 2024-07-10
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Screen for the curve feedback

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

from .base_experiment_screen import BaseExperimentScreen

from ..options import rop
from .. import logger


# %% ---- 2024-07-10 ------------------------
# Function and class
class CurveScreen(BaseExperimentScreen):
    '''
    Curve feedback screen
    '''
    # Curves and pens
    delayed_curve = None
    feedback_curve = None
    reference_curve = None

    delayed_pen = pg.mkPen(color='red')
    feedback_pen = pg.mkPen(color='blue')
    reference_pen = pg.mkPen(color='green')

    # Marker
    marker_text_item = pg.TextItem('????')
    marker_legend = None

    def __init__(self, design: dict, lcd_y, lcd_t, progress_bar, on_stop, **kwargs):
        super().__init__(design, lcd_y, lcd_t, progress_bar, on_stop)
        self.put_components()
        logger.debug('Initialized')

    def put_components(self):
        # Put curves
        self.delayed_curve = self.plot([], [], pen=self.delayed_pen)
        self.feedback_curve = self.plot([], [], pen=self.feedback_pen)
        self.reference_curve = self.plot([], [], pen=self.reference_pen)

        # Disable autorange
        self.disableAutoRange()

        # Legend for marker
        self.marker_legend = self.getPlotItem().addLegend(offset=(1, 1))

        # Resize the widget on device range changed
        self.sigDeviceRangeChanged.connect(self.on_size_changed)

        self.showGrid(x=True, y=True)
        return

    def on_size_changed(self):
        # Put marker and make it unmoving
        font = QFont()
        font.setPixelSize(40)
        self.marker_text_item.setFont(font)
        self.marker_text_item.setAnchor((0, 0))
        self.marker_text_item.setColor("red")
        self.marker_text_item.setPos(self.width()/2, self.height()/2)
        self.marker_text_item.setFlag(
            self.marker_text_item.GraphicsItemFlag.ItemIgnoresTransformations
        )
        self.marker_text_item.setParentItem(self.marker_legend)
        return

    def draw(self):
        self.frames += 1

        # Compute peek_length based on delayedLength option
        peek_length = np.max([10, rop.delayedLength*2])

        # Get data
        data = self.HID_reader.peek_by_seconds(peek_length, peek_delay=False)
        data = np.array(data)

        # Got no data, return
        if len(data) == 0:
            return

        # Set data
        real_y = data[:, 0]
        fake_y = data[:, 2]
        times = data[:, 4]
        ref_y = np.zeros(times.shape) + rop.yReference

        # Current time
        passed = times[-1]

        # Get the current block mark
        # - E: all the blocks are finished;
        # - O: running on no blocks model, it will never finished by itself;
        # - F: feedback with pseudo response.
        # - T: feedback with true response.
        # - +: feedback with no curve displaying.
        mark, remain_block, remain_total, remain_ratio = self.bm.consume(
            passed)
        self.marker_text_item.setText(mark)

        # If mark is E, execute the blocks finished process
        if mark == 'E':
            self.stop()

        if mark == 'F':
            self.feedback_curve.setData(times, self._limit(fake_y))
        else:
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
            if mark == 'F':
                self.delayed_curve.setData(d_times, self._limit(fake_d_y))
            else:
                self.delayed_curve.setData(d_times, self._limit(real_d_y))

        # Update the visible for the curves
        if mark == '+':
            # Set the visible for the curves by force
            self.delayed_curve.setVisible(False)
            self.feedback_curve.setVisible(False)
        else:
            # Set the visible for the curves according to options
            self.delayed_curve.setVisible(rop.flagDisplayDelayedCurve)
            self.feedback_curve.setVisible(rop.flagDisplayFeedbackCurve)
        self.reference_curve.setVisible(rop.flagDisplayReferenceCurve)

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
        self.lcd_y.display(f'{real_y[-1]:0.2f}')
        self.lcd_t.display(f'{times[-1]:0.2f}')

        # Set progress bar
        self.progress_bar.setValue(100*(1-remain_ratio))
        return


# %% ---- 2024-07-10 ------------------------
# Play ground


# %% ---- 2024-07-10 ------------------------
# Pending


# %% ---- 2024-07-10 ------------------------
# Pending
