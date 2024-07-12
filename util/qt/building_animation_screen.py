"""
File: building_animation_screen.py
Author: Chuncheng Zhang
Date: 2024-07-12
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Building up animation screen

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-12 ------------------------
# Requirements and constants
import numpy as np
import pyqtgraph as pg

from threading import Thread
from PySide2.QtGui import QFont

from .base_experiment_screen import BaseExperimentScreen
from ..animation.toolbox import pil2rgb
from ..options import rop
from .. import logger


# %% ---- 2024-07-12 ------------------------
# Function and class
class BuildingAnimationScreen(BaseExperimentScreen):
    '''
    Building up animation screen
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
    bsa = None

    def __init__(self, design: dict, lcd_y, lcd_t, progress_bar, on_stop, bsa, **kwargs):
        super().__init__(design, lcd_y, lcd_t, progress_bar, on_stop)
        self.put_components()

        # Load bsa and reset it
        self.bsa = bsa
        self.bsa.reset()
        logger.debug(f'Loaded bsa: {self.bsa}')

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

        self.bsa.width = self.width()
        self.bsa.height = self.height()
        return

    def draw(self):
        # Increase frames
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

        # Update image
        mat = pil2rgb(self.bsa.img)
        self.image_item.setImage(mat[::-1].transpose([1, 0, 2]))

        # Determine if update is required
        self.need_update_flag = passed > self.next_animation_update_seconds

        # Update and increase the next_animation_update_seconds
        if self.need_update_flag:
            self.next_animation_update_seconds += self.animation_time_step_length
            avg = pairs_delay[-1, 0]
            std = pairs_delay[-1, 1]
            score = self.update_animation_score(avg, std)
            Thread(target=self.bsa.mk_frames, args=(
                score,), daemon=True).start()

        # Set LED
        self.lcd_y.display(f'{real_y[-1]:0.2f}')
        self.lcd_t.display(f'{times[-1]:0.2f}')

        # Set progress bar
        self.progress_bar.setValue(100*(1-remain_ratio))
        return

    def update_animation_score(self, avg, std):
        if std > rop.thresholdOfStd:
            step = -10
        else:
            step = 10

        logger.debug(
            f"Compare animation feedback (std), {step}, {std}, {rop.thresholdOfStd}"
        )

        score = self.bsa.safe_update_score(step)

        logger.debug(f"Update score to: {score}, step: {step}")

        return score


# %% ---- 2024-07-12 ------------------------
# Play ground


# %% ---- 2024-07-12 ------------------------
# Pending


# %% ---- 2024-07-12 ------------------------
# Pending
