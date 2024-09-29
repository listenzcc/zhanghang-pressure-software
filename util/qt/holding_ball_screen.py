"""
File: holding_ball_screen.py
Author: Chuncheng Zhang
Date: 2024-07-11
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Screen for the holding ball feedback

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

from PIL import Image
from PySide2 import QtWidgets
from PySide2.QtGui import QFont

from .base_experiment_screen import BaseExperimentScreen

from ..options import rop
from .. import logger

root_path = rop.project_root

# %% ---- 2024-07-11 ------------------------
# Function and class


def convert_rgb_to_rgba(img, mask: np.ndarray = None):
    '''
    Convert rgb to rgba img.
    The (255, 255, 255) white color is converted to transparent.
    '''

    def _guess_mask():
        # Guess the mask from the given img
        # The transparent color is white (255, 255, 255)
        mat = np.sum(np.asarray(img), 2)
        mask = mat * 0 + 255
        mask[mat == 255*3] = 0
        return mask

    # Convert white color to transparent
    if mask is None:
        mask = _guess_mask()

    # Make the new array for the RGBA img
    mat = np.zeros((img.size[1], img.size[0], 4))
    mat[:, :, :3] = np.asarray(img)
    mat[:, :, 3] = mask

    # Return
    return Image.fromarray(mat.astype('uint8'), mode='RGBA')


class Balloon(object):
    raw_img = Image.open(root_path.joinpath(
        'asset/img/balloon/气球（没尾巴）.jpg'))
    reference_img = Image.open(root_path.joinpath(
        'asset/img/balloon/reference.png'))
    animating_img = convert_rgb_to_rgba(Image.open(root_path.joinpath(
        'asset/img/balloon/animating.png')))
    img: Image = None

    def __init__(self):
        self.img = self.raw_img.convert('RGB')

    def resize(self, width, height):
        size = (int(width), int(height))
        self.img = self.raw_img.resize(size).convert('RGB')
        self.reference_img = self.reference_img.resize(size)
        self.animating_img = self.animating_img.resize(size)
        return self.img

    def get_rgb(self):
        '''Get RGB matrix'''
        mat = np.array(self.img, dtype=np.uint8)
        return mat


balloon = Balloon()


class HoldingBallScreen(BaseExperimentScreen):
    # Img
    image_item = pg.ImageItem()

    # Ellipse and pens
    delayed_ellipse = QtWidgets.QGraphicsEllipseItem(-1, -1, 2, 2)
    feedback_ellipse = QtWidgets.QGraphicsEllipseItem(-1, -1, 2, 2)
    reference_ellipse = QtWidgets.QGraphicsEllipseItem(-1, -1, 2, 2)

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
        # Add the ellipse
        self.delayed_ellipse.setPen(self.delayed_pen)
        self.feedback_ellipse.setPen(self.feedback_pen)
        self.reference_ellipse.setPen(self.reference_pen)

        # mat = balloon.get_rgb()
        img = Image.composite(
            balloon.animating_img, balloon.reference_img, balloon.animating_img)
        mat = np.array(img.convert('RGB'))
        self.image_item.setImage(mat[::-1].transpose([1, 0, 2]))

        self.addItem(self.image_item)
        self.addItem(self.delayed_ellipse)
        self.addItem(self.feedback_ellipse)
        self.addItem(self.reference_ellipse)

        # Disable autorange
        # self.disableAutoRange()

        self.showGrid(x=True, y=True)

        # Legend for marker
        self.marker_legend = self.getPlotItem().addLegend(offset=(1, 1))

        # Resize the widget on device range changed
        self.sigDeviceRangeChanged.connect(self.on_size_changed)
        self.on_size_changed()

        return

    def on_size_changed(self):
        # Change range dynamically
        width = self.width()
        height = self.height()

        r = width / height
        k = np.min((width, height))
        k = 500

        # Change the xrange and the balloon img
        # The _xy_limit is updated automatically, since the self.width() and self.height() doesn't work well.
        if width > height:
            self.setYRange(-0, k)
            self.setXRange(-0*r, k*r)
            balloon.resize(k*r, k)
            self._xy_limit = (k*r, k)
        else:
            self.setXRange(-0, k)
            self.setYRange(-0/r, k/r)
            balloon.resize(k, k/r)
            self._xy_limit = (k, k/r)

        # mat = balloon.get_rgb()
        img = Image.composite(
            balloon.animating_img, balloon.reference_img, balloon.animating_img)
        mat = np.array(img.convert('RGB'))
        self.image_item.setImage(mat[::-1].transpose([1, 0, 2]))

        logger.debug(f'Changed range with width {width}, height {height}')

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

    def compute_ellipse_coordinates(self, ref, v):
        '''
        Convert y to ellipse coordinates

            - v == ref: 1
            - v > ref: 1 -> 0, exp(-d)
            - v < ref: 1 -> +infinity, 2-exp(-d)
        '''
        # self.update_range()
        # r = np.min((self.width(), self.height())) / 2
        width, height = self._xy_limit
        r = np.min(self._xy_limit)
        r *= 0.5

        # Compute normalized different between y and ref
        d = np.abs((v-ref) / ref)
        # Convert into coordinates
        if v > ref:
            k = np.exp(-d)
        else:
            k = 2 - np.exp(-d)
        k *= r

        x = -k
        y = -k
        w = 2 * k
        h = 2 * k

        x += width/2
        y += height/2

        return x, y, w, h

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

        ref = rop.yReference

        # Set data
        real_y = data[:, 0]
        fake_y = data[:, 2]
        times = data[:, 4]

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

        # Set the reference ellipse
        a, b, c, d = self.compute_ellipse_coordinates(ref, ref)
        self.reference_ellipse.setRect(a, b, c, d)

        # Compute coordinates and set rect
        y_value = fake_y[-1] if mark == 'F' else real_y[-1]
        a, b, c, d = self.compute_ellipse_coordinates(ref, y_value)
        self.feedback_ellipse.setRect(a, b, c, d)

        # Draw the balloon image
        # mat = balloon.get_rgb()
        k = int(((y_value - ref) / ref) * 500 * 0.4)
        img = balloon.reference_img.copy()
        sz = img.size
        img1 = balloon.animating_img.copy().resize((sz[0]-2*k, sz[1]+2*k))
        img.paste(img1, (k, -k), img1)
        # img = Image.composite(
        #     balloon.animating_img, balloon.reference_img, balloon.animating_img)
        mat = np.array(img.convert('RGB'))
        self.image_item.setImage(mat[::-1].transpose([1, 0, 2]))

        # Get delayed_data
        delayed_data = self.HID_reader.peek_by_seconds(
            peek_length, peek_delay=True)
        delayed_data = np.array(delayed_data)

        # Set delayed data
        if len(delayed_data) > 0:
            real_d_y = delayed_data[:, 0]
            fake_d_y = delayed_data[:, 1]
            d_times = delayed_data[:, 4]
            # Compute coordinates and set rect
            y_value = fake_d_y[-1] if mark == 'F' else real_d_y[-1]
            a, b, c, d = self.compute_ellipse_coordinates(
                ref, y_value)
            self.delayed_ellipse.setRect(a, b, c, d)

        # Update the visible for the curves
        if mark == '+':
            # Set the visible for the curves by force
            self.delayed_ellipse.setVisible(False)
            self.feedback_ellipse.setVisible(False)
        else:
            # Set the visible for the curves according to options
            self.delayed_ellipse.setVisible(rop.flagDisplayDelayedCurve)
            self.feedback_ellipse.setVisible(rop.flagDisplayFeedbackCurve)
        self.reference_ellipse.setVisible(rop.flagDisplayReferenceCurve)

        # Set Pen
        self.reference_pen.setColor(rop.referenceCurveColor)
        self.reference_pen.setWidth(rop.referenceCurveWidth)
        self.feedback_pen.setColor(rop.feedbackCurveColor)
        self.feedback_pen.setWidth(rop.feedbackCurveWidth)
        self.delayed_pen.setColor(rop.delayedCurveColor)
        self.delayed_pen.setWidth(rop.delayedCurveWidth)

        # Set LED
        self.lcd_y.display(f'{real_y[-1]:0.2f}')
        self.lcd_t.display(f'{times[-1]:0.2f}')

        # Set progress bar
        self.progress_bar.setValue(100*(1-remain_ratio))

# %% ---- 2024-07-11 ------------------------
# Play ground


# %% ---- 2024-07-11 ------------------------
# Pending


# %% ---- 2024-07-11 ------------------------
# Pending
