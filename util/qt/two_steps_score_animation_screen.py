"""
File: two_steps_score_animation_screen.py
Author: Chuncheng Zhang
Date: 2024-07-11
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Screen for cat climbing tree feedback

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-11 ------------------------
# Requirements and constants
import numpy as np
import pyqtgraph as pg

from PySide2.QtGui import QFont
from threading import Thread

from .base_experiment_screen import BaseExperimentScreen

from ..animation.toolbox import pil2rgb

from ..options import rop
from .. import logger

# %% ---- 2024-07-11 ------------------------
# Function and class


class TwoStepsScoreAnimationScreen(BaseExperimentScreen):
    '''
    Two steps score animation screen
    '''
    # Img
    image_item = pg.ImageItem()

    # Marker
    marker_text_item = pg.TextItem('')
    marker_legend = None

    # Update timer stuff
    need_update_flag = True
    animation_time_step_length = 3  # seconds
    next_animation_update_seconds = 0

    # Animation stuff
    tssa = None

    def __init__(self, design: dict, lcd_y, lcd_t, progress_bar, on_stop, tssa, **kwargs):
        super().__init__(design, lcd_y, lcd_t, progress_bar, on_stop)
        self.put_components()

        # Load the animation stuff
        self.tssa = tssa
        # Reset the animation
        self.tssa.reset()
        mat = pil2rgb(self.tssa.welcome_img)
        # Transpose the shape for the matrix
        self.image_item.setImage(mat[::-1].transpose([1, 0, 2]))
        logger.debug(f'Loaded tssa {self.tssa}')

        self.next_animation_update_seconds = 0

        logger.info('Initialized')

    def put_components(self):
        # Put image
        self.addItem(self.image_item)

        # Legend for marker
        self.marker_legend = self.getPlotItem().addLegend(offset=(1, 1))

        # Resize the widget on device range changed
        self.sigDeviceRangeChanged.connect(self.on_size_changed)

        # Hide axis
        self.getPlotItem().hideAxis('bottom')
        self.getPlotItem().hideAxis('left')

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

        self.tssa.width = self.width()
        self.tssa.height = self.height()
        return

    def draw(self):
        self.frames += 1

        # Compute peek_length based on delayedLength option
        peek_length = np.max([10, rop.delayedLength*2])

        # Get data
        data = self.HID_reader.peek_by_seconds(peek_length, peek_delay=False)
        data = np.array(data)

        # Get delayed_data
        delayed_data = self.HID_reader.peek_by_seconds(
            peek_length, peek_delay=True)
        delayed_data = np.array(delayed_data)

        # Got no data, return
        if len(data) == 0 or len(delayed_data) == 0:
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

        # On fake feedback block, using fake data
        # On other feedback block, using real data
        if mark == 'F':
            pairs_delay = delayed_data[:, (1, 3, 4)]
        else:
            pairs_delay = delayed_data[:, (0, 2, 4)]
        pairs_delay = pairs_delay.tolist()

        # Always update the tiny window
        # Draw the tiny window for pressure feedback
        mat = pil2rgb(self.tssa.tiny_window(
            ref=rop.yReference, data=pairs_delay, block_name=mark))
        # Transpose the shape for the matrix
        self.image_item.setImage(mat[::-1].transpose([1, 0, 2]))

        # Determine if update is required
        self.need_update_flag = passed > self.next_animation_update_seconds

        # Update and increase the next_animation_update_seconds
        if self.need_update_flag:
            self.next_animation_update_seconds += self.animation_time_step_length

            # Update parameters
            self.tssa.mean_threshold = rop.thresholdOfMean
            self.tssa.std_threshold = rop.thresholdOfStd
            self.tssa.ref_value = rop.yReference

            Thread(
                target=self.tssa.update_score,
                args=(pairs_delay, mark), daemon=True).start()

        # Set LED
        self.lcd_y.display(f'{real_y[-1]:0.2f}')
        self.lcd_t.display(f'{times[-1]:0.2f}')

        # Set progress bar
        self.progress_bar.setValue(100*(1-remain_ratio))
        return

# %% ---- 2024-07-11 ------------------------
# Play ground


# %% ---- 2024-07-11 ------------------------
# Pending


# %% ---- 2024-07-11 ------------------------
# Pending
