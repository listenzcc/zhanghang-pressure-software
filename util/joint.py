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


import contextlib
# %% ---- 2024-07-09 ------------------------
# Requirements and constants
import json
from pathlib import Path
from datetime import datetime
from PySide2 import QtCore, QtWidgets

from .qt.load_ui import MainWindow, app

from .qt.curve_screen import CurveScreen
from .qt.replay_screen import ReplayScreen
from .qt.welcome_screen import WelcomeScreen
from .qt.holding_ball_screen import HoldingBallScreen
from .qt.building_animation_screen import BuildingAnimationScreen
from .qt.two_steps_score_animation_screen import TwoStepsScoreAnimationScreen

from .animation.two_steps_score_animation import TwoStepScore_Animation_CatClimbsTree
from .animation.two_steps_score_animation import TwoStepScore_Animation_CatLeavesSubmarine
from .animation.score_animation import BuildingScoreAnimation

from .feedback_mode_enum import FeedbackModeEnum, get_feedback_mode_info
from .options import rop
from . import logger

mw = MainWindow()

bsa = BuildingScoreAnimation()
tssa_cct = TwoStepScore_Animation_CatClimbsTree()
tssa_cls = TwoStepScore_Animation_CatLeavesSubmarine()

# %% ---- 2024-07-09 ------------------------
# Function and class


def _load_feedback_modes():
    '''
    Load the feedback modes to the comboBox
    '''
    box_name = 'zcc_comboBox_modeSelection'
    box = mw.children[box_name]

    for e in FeedbackModeEnum:
        s = get_feedback_mode_info(e)
        box.addItem(s, userData=e)
        logger.debug(f'Loaded feedback mode {s}')

    def update_feedback_model():
        # Set the option with the userRole(userData)
        rop.feedback_model = box.currentData()
        logger.debug(f'Set feedbackMode to {e}')

    box.currentIndexChanged.connect(update_feedback_model)

    # Initialize with the current value
    update_feedback_model()

    return


def _bind_toggle(widget: QtWidgets.QCheckBox, attr_name: str):
    '''
    Bind the checkBox widget to the option
    '''
    # Set the widget value to the rop option
    widget.setChecked(rop.__getattribute__(attr_name))

    # The rop option follows the widget changing
    def _handle_change(value):
        rop.__setattr__(attr_name, value)
        logger.debug(f'Set {attr_name} to {value}')

    widget.stateChanged.connect(_handle_change)
    logger.debug(f'Linked {attr_name} with {widget}')


def _bind_number(widget: QtWidgets.QAbstractSpinBox, attr_name: str):
    '''
    Bind the number spin widget to the option
    '''
    # Set the widget value to the rop option
    widget.setValue(rop.__getattribute__(attr_name))

    # The rop option follows the widget changing
    def _handle_change(value):
        rop.__setattr__(attr_name, value)
        logger.debug(f'Set {attr_name} to {value}')

    widget.valueChanged.connect(_handle_change)
    logger.debug(f'linked {attr_name} with {widget}')


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
            return a or b

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
        f'# Using fake pressure data: {rop.fake_file_path}',
        f'# Using design: {posix}',
        f'# Short path:   {short_posix}',
        f'# Name:         {dct["name"]}',
        f'# Maker:        {dct["maker"]}',
        f'# Total length: {total_length} seconds',
        '# Blocks as following:',
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


def _go_back_to_welcome_screen():
    '''
    Go back to welcome screen, it is designed to be executed on the stop for experiment processing
    '''
    pushButton_name_start = 'zcc_pushButton_start'
    pushButton_name_stop = 'zcc_pushButton_stop'

    # Make a new timer
    timer = mw.stop_timer_and_get_timer()

    # Put the welcome screen
    wel_screen = WelcomeScreen()
    wel_screen.start()
    timer.timeout.connect(wel_screen.draw)
    timer.start()
    mw.change_main_screen(wel_screen)

    # Disable this and release start pushButton
    mw.children[pushButton_name_start].setDisabled(True)
    mw.children[pushButton_name_stop].setDisabled(False)

    logger.debug('Went back to welcome screen')
    return


def start_experiment():
    # Get subject information
    rop.subjectName = mw.children['zcc_lineEdit_subjectName'].text()
    rop.subjectAge = mw.children['zcc_spinBox_subjectAge'].value()
    rop.subjectRem = mw.children['zcc_plainTextEdit_subjectOthers'].toPlainText(
    )
    rop.subjectExperimentDateTime = datetime.strftime(
        datetime.now(), '%Y-%m-%d-%H-%M-%S')
    if mw.children['zcc_radioButton_subjectGenderMale'].isChecked():
        rop.subjectGender = 'Male'
    else:
        rop.subjectGender = 'Female'
    logger.debug(f'''Subject information:
        {rop.subjectName},
        {rop.subjectGender},
        {rop.subjectAge},
        {rop.subjectExperimentDateTime},
        {rop.subjectRem}''')

    # Choose a screen object
    kwargs = {}
    if rop.feedback_model == FeedbackModeEnum.curveFeedback:
        Screen = CurveScreen
    elif rop.feedback_model == FeedbackModeEnum.holdingBallFeedback:
        Screen = HoldingBallScreen
    elif rop.feedback_model == FeedbackModeEnum.catClimbTreeFeedback:
        Screen = TwoStepsScoreAnimationScreen
        kwargs['tssa'] = tssa_cct
    elif rop.feedback_model == FeedbackModeEnum.catOutOceanFeedback:
        Screen = TwoStepsScoreAnimationScreen
        kwargs['tssa'] = tssa_cls
    elif rop.feedback_model == FeedbackModeEnum.buildingUpFeedback:
        Screen = BuildingAnimationScreen
        kwargs['bsa'] = bsa
    else:
        Screen = None
        logger.error(f'Invalid feedback mode: {rop.feedback_model}')
        return

    # Get block design
    design = rop.design
    logger.debug(f'Starting experiment: {design}')

    # Make a new timer
    timer = mw.stop_timer_and_get_timer()

    # Put the screen
    screen = Screen(
        design=design,
        lcd_y=mw.children['zcc_lcdNumber_yValue'],
        lcd_t=mw.children['zcc_lcdNumber_passedLength'],
        progress_bar=mw.children['zcc_progressBar_experimentProgress'],
        on_stop=_go_back_to_welcome_screen,
        **kwargs
    )
    screen.start()
    timer.timeout.connect(screen.draw)
    timer.start()
    mw.change_main_screen(screen)

    # Disable this and release stop pushButton
    pushButton_name_start = 'zcc_pushButton_start'
    pushButton_name_stop = 'zcc_pushButton_stop'
    mw.children[pushButton_name_start].setDisabled(True)
    mw.children[pushButton_name_stop].setDisabled(False)

    logger.debug(f'Started experiment: {design}')
    return


def _handle_start_pushButton():
    '''
    Handle the pushButton for start block design experiment
    '''
    # Connect
    pushButton_name_start = 'zcc_pushButton_start'
    mw.children[pushButton_name_start].clicked.connect(start_experiment)
    return


def stop_experiment():
    logger.debug('Stopping experiment')

    # Stop the current main_screen
    mw.main_screen_widget.stop()

    # Disable this and release start pushButton
    pushButton_name_start = 'zcc_pushButton_start'
    pushButton_name_stop = 'zcc_pushButton_stop'
    mw.children[pushButton_name_stop].setDisabled(True)
    mw.children[pushButton_name_start].setDisabled(False)

    logger.debug('Stopped experiment')


def _handle_stop_pushButton():
    '''
    Handle the pushButton for stop block design experiment
    '''

    # Connect
    pushButton_name_stop = 'zcc_pushButton_stop'
    mw.children[pushButton_name_stop].clicked.connect(stop_experiment)
    # Disable this on the app start
    mw.children[pushButton_name_stop].setDisabled(True)


def _place_welcomeScreen_to_hBox():
    '''
    Place the main screen to its place
    '''
    timer = mw.stop_timer_and_get_timer()
    wel_screen = WelcomeScreen()
    wel_screen.start()
    timer.timeout.connect(wel_screen.draw)
    timer.start()
    mw.change_main_screen(wel_screen)


# %% ---- 2024-07-09 ------------------------
# Play ground


# Place welcomeScreen for startup
_place_welcomeScreen_to_hBox()

# ----------------------------------------
# ---- Bind functions ----
# Handling experiment design buttons
_handle_loading_existing_design()
_handle_block_design_pushButtons()

# Handling controlling buttons
_handle_start_pushButton()
_handle_stop_pushButton()

# ----------------------------------------
# ---- Put feedback modes ----
_load_feedback_modes()

# ----------------------------------------
# ---- Bind numbers ----
# Display panel
_bind_number(mw.children['zcc_doubleSpinBox_yMax'], 'yMax')
_bind_number(mw.children['zcc_doubleSpinBox_yMin'], 'yMin')
_bind_number(mw.children['zcc_doubleSpinBox_yReference'], 'yReference')
_bind_number(
    mw.children['zcc_spinBox_feedbackCurveWidth'], 'feedbackCurveWidth')
_bind_number(
    mw.children['zcc_spinBox_referenceCurveWidth'], 'referenceCurveWidth')
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
_bind_number(
    mw.children['zcc_doubleSpinBox_metricThreshold1_2'], 'metricThreshold1_2')
_bind_number(
    mw.children['zcc_doubleSpinBox_metricThreshold2_2'], 'metricThreshold2_2')
_bind_number(
    mw.children['zcc_doubleSpinBox_metricThreshold3_2'], 'metricThreshold3_2')


# ----------------------------------------
# ---- Bind colors ----
_bind_color(
    mw.children['zcc_pushButton_feedbackCurveColor'], 'feedbackCurveColor')
_bind_color(
    mw.children['zcc_pushButton_referenceCurveColor'], 'referenceCurveColor')
_bind_color(
    mw.children['zcc_pushButton_delayedCurveColor'], 'delayedCurveColor')


# ----------------------------------------
# ---- Bind toggles ----
_bind_toggle(
    mw.children['zcc_checkBox_flagDisplayFeedbackCurve'], 'flagDisplayFeedbackCurve')
_bind_toggle(
    mw.children['zcc_checkBox_flagDisplayReferenceCurve'], 'flagDisplayReferenceCurve')
_bind_toggle(
    mw.children['zcc_checkBox_flagDisplayDelayedCurve'], 'flagDisplayDelayedCurve')

# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
# Handle keypress
# F11 key code is 16777274
known_key_code = {
    16777274: 'F11',
    16777216: 'Esc',
    83: 's'
}


class KeyPressFilter(QtCore.QObject):
    def eventFilter(self, widget, event):
        # Return False if it is not a KeyPress
        if event.type() != QtCore.QEvent.KeyPress:
            return False

        # It is a KeyPress event, do something
        key_code = event.key()
        text = event.text()
        if event.modifiers():
            text = event.keyCombination().key().name.decode(encoding="utf-8")
        logger.debug(f'Key pressed: {key_code}, {text}, {event}')

        # F11 is pressed, toggle full screen display
        if known_key_code.get(key_code) == 'F11':
            logger.debug('Got F11 pressed')
            toggle_full_screen_display()

        # Esc is pressed, exit the application
        if known_key_code.get(key_code) == 'Esc':
            logger.debug('Got Esc pressed')
            try:
                stop_experiment()
            finally:
                app.exit()

        # s is pressed, toggle start and stop experiment
        if known_key_code.get(key_code) == 's':
            logger.debug('Got s pressed')
            try:
                name = mw.main_screen_widget.name
            except Exception:
                name = 'no-named-screen'
            finally:
                if name == 'Experiment screen':
                    logger.debug(
                        'Stop experiment since the experiment screen is running.')
                    stop_experiment()
                else:
                    logger.debug(
                        f'Start experiment since the {name} is running.')
                    start_experiment()

        return True


# Add event handler
eventFilter = KeyPressFilter(parent=mw.window)
# Install the event filter
mw.window.installEventFilter(eventFilter)


def toggle_full_screen_display():
    if QtCore.Qt.WindowFullScreen & mw.window.windowState():
        # from showFullScreen to showNormal
        mw.window.showNormal()
        mw.children['zcc_leftFrame'].setVisible(True)
        mw.children['zcc_bottomFrame'].setVisible(True)

        # Restore where the stuff were located.
        mw.middle_frame.setGeometry(mw.middle_frame_geometry)
        mw.main_screen_container.setGeometry(mw.main_screen_container_geometry)

        logger.debug('Entered show normal state')
    else:
        # from showNormal to showFullScreen
        mw.window.showFullScreen()
        mw.children['zcc_leftFrame'].setVisible(False)
        mw.children['zcc_bottomFrame'].setVisible(False)

        # Remember where the stuff are located.
        mw.main_screen_container_geometry = mw.main_screen_container.geometry()
        mw.middle_frame_geometry = mw.middle_frame.geometry()

        # Full screen them
        win_geometry = mw.window.geometry()
        mw.middle_frame.setGeometry(win_geometry)
        mw.main_screen_container.setGeometry(win_geometry)

        logger.debug('Entered show full screen state')


mw.children['zcc_pushButton_toggleFullScreen'].clicked.connect(
    toggle_full_screen_display)

# %%


def _on_click_playback_button():
    # Read the existing data
    file, _ = QtWidgets.QFileDialog().getOpenFileName(
        caption='Read protocol',
        dir=rop.project_root.joinpath('Data/Data').as_posix(),
        filter="Json files (*.json)")

    # Go on only when the file is not empty
    if not file:
        logger.warning('Not selecting any file')
        return

    path = Path(file)
    data = json.load(open(path))

    # Make a new timer
    timer = mw.stop_timer_and_get_timer()

    # Put the screen
    screen = ReplayScreen(data, path)
    screen.draw()
    timer.timeout.connect(screen.draw)
    timer.start()
    mw.change_main_screen(screen)

    # Disable stop pushButton and release start pushButton
    pushButton_name_start = 'zcc_pushButton_start'
    pushButton_name_stop = 'zcc_pushButton_stop'
    mw.children[pushButton_name_stop].setDisabled(True)
    mw.children[pushButton_name_start].setDisabled(False)


mw.children['zcc_pushButton_replayCurve'].clicked.connect(
    _on_click_playback_button)

# %%


def _on_click_load_fake_feedback_data_button():
    # Read the existing data
    file, _ = QtWidgets.QFileDialog().getOpenFileName(
        caption='Read protocol',
        dir=rop.project_root.joinpath('Data/Data').as_posix(),
        filter="Json files (*.json)")

    # Go on only when the file is not empty
    if not file:
        logger.warning('Not selecting any file')
        return

    # Set rop's fake_file_path attribute
    path = Path(file)
    rop.fake_file_path = path
    logger.debug(f'Change fake_file_path to {path}')

    # Update the experiment design part immediately
    _update_experimentDesign(rop.design)


mw.children['zcc_pushButton_loadFakeFeedback'].clicked.connect(
    _on_click_load_fake_feedback_data_button)

# %%


def _handle_education_mode_radioButton():
    name = 'zcc_radioButton_educationMode'

    def _on_click():
        rop.education_mode_flag = mw.children[name].isChecked()
        logger.debug(f'Set education_mode_flat to {rop.education_mode_flag}')
    mw.children[name].clicked.connect(_on_click)


_handle_education_mode_radioButton()

# %%


def _handle_correction_pushButtons():
    name_offsetG0 = 'zcc_pushButton_zeroOffset'
    name_g0 = 'zcc_pushButton_0gPressure'
    name_g200 = 'zcc_pushButton_200gPressure'

    def _offsetG0():
        with contextlib.suppress(Exception):
            mw.main_screen_widget._correction_offset_0g()

    def _correlation_g0():
        with contextlib.suppress(Exception):
            mw.main_screen_widget._correction_0g()

    def _correlation_g200():
        with contextlib.suppress(Exception):
            mw.main_screen_widget._correction_200g()

    mw.children[name_offsetG0].clicked.connect(_offsetG0)
    mw.children[name_g0].clicked.connect(_correlation_g0)
    mw.children[name_g200].clicked.connect(_correlation_g200)


_handle_correction_pushButtons()
