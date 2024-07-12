"""
File: replay_screen.py
Author: Chuncheng Zhang
Date: 2024-07-12
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Simple screen for replaying data

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

from PySide2.QtGui import QFont

from ..options import rop
from .. import logger

# %% ---- 2024-07-12 ------------------------
# Function and class


class ReplayScreen(pg.PlotWidget):
    # Basic setup
    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")
    pg.setConfigOption("antialias", True)

    # Items
    marker_text_item = pg.TextItem(color=(0, 0, 0))
    marker_legend = None

    curve = None
    curve_pen = pg.mkPen(color='black')

    # Data
    data = None
    path = None

    # Screen name
    name = 'Replay screen'

    def __init__(self, data, path):
        super().__init__()
        self.data = np.array(data)
        self.path = path
        self.curve = self.plot([], [], pen=self.curve_pen)
        self.showGrid(x=True, y=True)

        # Legend for marker
        self.marker_legend = self.getPlotItem().addLegend(offset=(1, 1))

        # Resize the widget on device range changed
        self.sigDeviceRangeChanged.connect(self.on_size_changed)

    def on_size_changed(self):
        # Put marker and make it unmoving
        font = QFont()
        font.setPixelSize(16)
        self.marker_text_item.setFont(font)
        self.marker_text_item.setAnchor((0, 0))
        self.marker_text_item.setColor("#302020")
        self.marker_text_item.setPos(0, 0)  # self.width()/2, self.height()/2)
        self.marker_text_item.setFlag(
            self.marker_text_item.GraphicsItemFlag.ItemIgnoresTransformations
        )
        self.marker_text_item.setParentItem(self.marker_legend)
        return

    def start(self):
        logger.debug('Start')

    def stop(self):
        logger.debug('Stop')

    def restart(self):
        logger.debug('restart')

    def draw(self):
        y = self.data[:, 0]
        t = self.data[:, -1]
        self.curve.setData(t, y)
        self.marker_text_item.setText(f'{self.path}\n{self.path.name}')
        return


# %% ---- 2024-07-12 ------------------------
# Play ground


# %% ---- 2024-07-12 ------------------------
# Pending


# %% ---- 2024-07-12 ------------------------
# Pending
