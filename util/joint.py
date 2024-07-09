"""
File: joint.py
Author: Chuncheng Zhang
Date: 2024-07-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Joint the window and the components

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-09 ------------------------
# Requirements and constants
import json
from pathlib import Path
from PySide2 import QtWidgets

from .qt.load_ui import MainWindow
from .qt.screen import MainScreen

from .options import rop
from . import logger

mw = MainWindow()
ms = MainScreen()

# %% ---- 2024-07-09 ------------------------
# Function and class


def _bind_number(widget: QtWidgets.QAbstractSpinBox, attr_name: str):
    '''
    Bind the number widgets to the options
    '''
    # Set the widget value to the rop option
    widget.setValue(rop.__getattribute__(attr_name))

    # The rop option follows the widget changing
    def _handle_change(value):
        rop.__setattr__(attr_name, value)

    widget.valueChanged.connect(_handle_change)
    logger.debug(f'Handled {attr_name} with {widget}')


def _bind_color(widget: QtWidgets.QPushButton, attr_name: str):
    '''
    Bind the color widgets to the options.
    Its face color refers to the color.
    '''
    # Set the widget value to the rop option
    widget.setStyleSheet(
        "QPushButton {background-color: " + rop.__getattribute__(attr_name) + "}")

    # The rop option follows the widget changing
    def _handle_click():
        # Get current color
        c = rop.__getattribute__(attr_name)
        # Ask for the new color (initialized with the current color)
        c = QtWidgets.QColorDialog().getColor(c)
        # If the output color is valid,
        # update both the face color and option
        if c.isValid():
            hexRgb = '#' + ''.join(
                hex(e).replace('x', '')[-2:]
                for e in [c.red(), c.green(), c.blue()])
            rop.__setattr__(attr_name, hexRgb)
            widget.setStyleSheet(
                "QPushButton {background-color: " + hexRgb + "}")

    widget.clicked.connect(_handle_click)
    logger.debug(f'Handled {attr_name} with {widget}')


def _update_experimentDesign(dct: dict, p: Path = None):
    # Put the experiment design content to the textBrowser
    textBrowser_name = 'zcc_textBrowser_experimentDesign'

    # Notion if the path is valid,
    # it refers if the dct is read from a file
    try:
        posix = p.as_posix()
        short_posix = '/'.join(
            e[0] for e in p.as_posix()[:-1].split('/')) + f'/{p.name}'

    except Exception:
        def _aOrB(ab):
            a, b = ab
            return a if a else b

        posix = 'Cached'
        short_posix = 'Cached'
        # The dct is not from a file, so update it with the current contents
        dct['name'] = _aOrB([
            mw.children['zcc_lineEdit_designName'].text(),
            mw.children['zcc_lineEdit_designName'].placeholderText()
        ])
        dct['maker'] = _aOrB([
            mw.children['zcc_lineEdit_designMaker'].text(),
            mw.children['zcc_lineEdit_designMaker'].placeholderText()
        ])

    # Compute the blocks
    total_length = 0
    block_lines = []
    n = len(dct['_buffer'])
    for i, (block_name, block_length) in enumerate(dct['_buffer']):
        block_lines.append(
            f'[{i+1} | {n}] >> {block_name}: {block_length} seconds')
        total_length += block_length

    lines = [
        f'# Using design: {posix}',
        f'# Short path:   {short_posix}',
        f'# Name:         {dct["name"]}',
        f'# Maker:        {dct["maker"]}',
        f'# Total length: {total_length} seconds',
        f'# Blocks as following:'
    ]

    lines.extend(block_lines)
    mw.children[textBrowser_name].setText('\n'.join(lines))
    logger.debug(
        f'Updated block design to {textBrowser_name}: {dct} from {posix}')

    rop.design = dct
    logger.debug(f'Updated block design to {rop}')


def _handle_loading_existing_design():
    '''
    Handle the pushButton of loading existing block design
    '''
    pushButton_name = 'zcc_pushButton_loadPreDesign'

    # Update the design from the default design as the rop writes
    _update_experimentDesign(rop.design)

    def _load():
        # Read the existing design
        file, _ = QtWidgets.QFileDialog().getOpenFileName(
            caption='Read protocol',
            dir=rop.project_root.joinpath('Protocols').as_posix(),
            filter="Json files (*.json)")
        # Go on if and only if file is not empty
        if file:
            p = Path(file)
            dct = json.load(open(p, encoding='utf-8'))
            _update_experimentDesign(dct, p)
        else:
            logger.warning('Not selecting any file')

    mw.children[pushButton_name].clicked.connect(_load)
    logger.debug(f'Handled {pushButton_name}')


def _handle_block_design_pushButtons():
    '''
    Handle the pushButtons for block design
    '''
    def _add_real_block():
        rop.design['_buffer'].append(['Real', rop.blockLength])
        _update_experimentDesign(rop.design)

    def _add_fake_block():
        rop.design['_buffer'].append(['Fake', rop.blockLength])
        _update_experimentDesign(rop.design)

    def _add_hide_block():
        rop.design['_buffer'].append(['Hide', rop.blockLength])
        _update_experimentDesign(rop.design)

    def _repeat_blocks():
        rop.design['_buffer'].extend(rop.design['_buffer'])
        _update_experimentDesign(rop.design)

    def _clear_blocks():
        rop.design['_buffer'] = []
        _update_experimentDesign(rop.design)

    def _save_block_design():
        file, _ = QtWidgets.QFileDialog().getSaveFileName(
            caption='Save protocol',
            dir=rop.project_root.joinpath('Protocols').as_posix(),
            filter="Json file (*.json)")

        if file:
            json.dump(rop.design, open(file, 'w'))
        else:
            logger.warning('Not selected any file')

    mw.children['zcc_pushButton_appendRealBlock'].clicked.connect(
        _add_real_block)
    mw.children['zcc_pushButton_appendFakeBlock'].clicked.connect(
        _add_fake_block)
    mw.children['zcc_pushButton_appendHideBlock'].clicked.connect(
        _add_hide_block)

    mw.children['zcc_pushButton_repeatBlocks'].clicked.connect(_repeat_blocks)
    mw.children['zcc_pushButton_clearBlocks'].clicked.connect(_clear_blocks)
    mw.children['zcc_pushButton_saveCurrentDesign'].clicked.connect(
        _save_block_design)


def _handle_start_pushButton():
    '''
    Handle the pushButton for start block design experiment
    '''
    pushButton_name = 'zcc_pushButton_start'

    def _start_experiment():
        design = rop.design
        # TODO: Start the design experiment as the design requires
        logger.debug(f'Starting experiment: {design}')

    mw.children[pushButton_name].clicked.connect(_start_experiment)


def _handle_stop_pushButton():
    '''
    Handle the pushButton for stop block design experiment
    '''
    pushButton_name = 'zcc_pushButton_stop'

    def _stop_experiment():
        # TODO: Stop the running block design experiment
        logger.debug('Stop experiment')

    mw.children[pushButton_name].clicked.connect(_stop_experiment)


def _handle_toggleFullScreen_pushButton():
    '''
    Handle the pushButton for toggle full screen display
    '''
    pushButton_name = 'zcc_pushButton_toggleFullScreen'

    def _toggle_fullScreen_display():
        # TODO: Toggle the full screen display for the 'zcc_graphicsView_monitor'
        logger.debug('Toggle full screen display')

    mw.children[pushButton_name].clicked.connect(_toggle_fullScreen_display)


# Handling experiment design buttons
_handle_loading_existing_design()
_handle_block_design_pushButtons()

# Handling controlling buttons
_handle_start_pushButton()
_handle_stop_pushButton()
_handle_toggleFullScreen_pushButton()

# %% ---- 2024-07-09 ------------------------
# Play ground


# ----------------------------------------
# ---- Bind numbers ----
# Display panel
_bind_number(mw.children['zcc_doubleSpinBox_yMax'], 'yMax')
_bind_number(mw.children['zcc_doubleSpinBox_yMin'], 'yMin')
_bind_number(mw.children['zcc_doubleSpinBox_yReference'], 'yReference')
_bind_number(
    mw.children['zcc_spinBox_feedbackCurveWidth'], 'feedbackCurveWidth')
_bind_number(
    mw.children['zcc_spinBox_referenceCurveWidth'], 'feedbackCurveWidth')
_bind_number(
    mw.children['zcc_spinBox_delayedCurveWidth'], 'delayedCurveWidth')
_bind_number(
    mw.children['zcc_doubleSpinBox_delayedLength'], 'delayedLength')
_bind_number(
    mw.children['zcc_doubleSpinBox_updateStepLength'], 'updateStepLength')
_bind_number(
    mw.children['zcc_doubleSpinBox_thresholdOfMean'], 'thresholdOfMean')
_bind_number(
    mw.children['zcc_doubleSpinBox_thresholdOfStd'], 'thresholdOfStd')

# Block design panel
_bind_number(
    mw.children['zcc_spinBox_blockLength'], 'blockLength')
_bind_number(
    mw.children['zcc_doubleSpinBox_metricThreshold1'], 'metricThreshold1')
_bind_number(
    mw.children['zcc_doubleSpinBox_metricThreshold2'], 'metricThreshold2')
_bind_number(
    mw.children['zcc_doubleSpinBox_metricThreshold3'], 'metricThreshold3')

# ----------------------------------------
# ---- Bind colors ----

_bind_color(
    mw.children['zcc_pushButton_feedbackCurveColor'], 'feedbackCurveColor')
_bind_color(
    mw.children['zcc_pushButton_referenceCurveColor'], 'referenceCurveColor')
_bind_color(
    mw.children['zcc_pushButton_delayedCurveColor'], 'delayedCurveColor')

# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
