"""
File: welcome_screen.py
Author: Chuncheng Zhang
Date: 2024-07-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    The screens on display

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-09 ------------------------
# Requirements and constants
import pyqtgraph as pg

from PySide2.QtGui import QFont

from .performance_ruler import PerformanceRuler
from .. import logger


# %% ---- 2024-07-09 ------------------------
# Function and class
class DrawingToolbox(object):
    black_pen = pg.mkPen(color='black')
    red_pen = pg.mkPen(color='red')
    font = QFont()

    def __init__(self):
        self.font.setPixelSize(20)


class WelcomeScreen(pg.GraphicsLayoutWidget):
    # Basic setup
    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")
    pg.setConfigOption("antialias", True)

    # Image item
    image_item = pg.ImageItem()
    text_item = pg.TextItem(color=(0, 0, 0))
    score_curve = None
    fps_curve = None

    # Performance ruler
    pr = PerformanceRuler()

    # Toolbox
    dtb = DrawingToolbox()

    # Layout
    plot00 = None
    plot01 = None
    plot10 = None
    plot11 = None

    def __init__(self):
        super().__init__()
        self._put_components()
        logger.info('Initialized')

    def _create_layout(self):
        self.plot00 = self.addPlot(row=0, col=0, colspan=2)
        self.plot10 = self.addPlot(row=1, col=0)
        self.plot11 = self.addPlot(row=1, col=1)
        logger.debug('Created layout plots')
        return

    def _put_components(self):
        self._create_layout()

        # Put image_item
        self.plot00.addItem(self.image_item)
        logger.debug(f'Put {self.image_item}')

        # Put score_curve
        self.score_curve = self.plot10.plot([], [], pen=self.dtb.black_pen)
        self.plot10.addItem(self.score_curve)
        logger.debug(f'Put {self.score_curve}')

        # Plot fps_curve
        self.fps_curve = self.plot11.plot([], [], pen=self.dtb.red_pen)
        self.plot11.addItem(self.fps_curve)
        logger.debug(f'Put {self.fps_curve}')

        # Plot text_item
        self.plot11.addItem(self.text_item)
        self.text_item.setText('Fps')
        self.text_item.setFont(self.dtb.font)
        logger.debug(f'Put {self.text_item}')

        return

    def draw(self):
        # Quick shot
        mat, scores = self.pr.get_quick_shot()

        # Draw the image
        self.image_item.setImage(mat)

        # Draw the running curve
        if len(scores) > 0:
            ts = scores[:, 0]
            score = scores[:, 1]
            fps = scores[:, 2]
            self.score_curve.setData(ts, score)
            self.fps_curve.setData(ts, fps)
            self.text_item.setText(f'Computing fps: {fps[-1]:0.2f} Hz')

            passed = ts[-1]
            if passed > 10:
                self.restart()

        return

    def start(self):
        self.pr.init_population()
        self.pr.start_update()
        logger.debug('Started pr')
        return

    def stop(self):
        self.pr.stop_update()
        logger.debug('Stopped pr')

    def restart(self):
        self.stop()
        self.start()
        return


# %% ---- 2024-07-09 ------------------------
# Play ground


# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
