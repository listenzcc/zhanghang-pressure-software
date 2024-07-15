"""
File: load_ui.py
Author: Chuncheng Zhang
Date: 2024-07-09
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


# %% ---- 2024-07-09 ------------------------
# Requirements and constants
import sys
from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader

from .. import logger
from ..options import rop


# %% ---- 2024-07-09 ------------------------
# Function and class

# QWidget: Must construct a QApplication before a QWidget
app = QtWidgets.QApplication(sys.argv)


class MainWindow(object):
    """
    Initializes the MainWindow object with a QtWidgets window and searches for children elements starting with 'zcc_'.
    """
    # The application
    app = app
    # The path of the UI design
    ui_path = rop.ui_path
    # The components of interest
    known_component_prefix = rop.known_components_prefix
    # Window title
    window_title = rop.project_name

    # The window object
    window = QUiLoader().load(ui_path.as_posix(), parentWidget=None)

    # The found components
    children = None

    # Make a timer
    timer = None

    # Current main screen widget
    middle_frame = None
    middle_frame_geometry = None
    main_screen_container = None
    main_screen_container_geometry = None
    main_screen_widget = None

    def __init__(self):
        self._search_children()
        self._assign_children()
        self._set_window_title()

        # ! I know it is not quit a elegant solution since the name is here
        self.middle_frame = self.children['zcc_middleFrame']
        layout = QtWidgets.QHBoxLayout(self.window)
        self.middle_frame.setLayout(layout)
        self.main_screen_container = layout

        # Only use the window close button
        self.window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

    def toggle_full_screen_display(self):
        if QtCore.Qt.WindowFullScreen & self.windowState():
            # is showFullScreen
            self.showNormal()
            logger.debug('Entered show normal state')
        else:
            # is not showFullScreen
            self.showFullScreen()
            logger.debug('Entered show full screen state')

    def change_main_screen(self, pg_widget):
        # Remove the exiting main screen widget with the new one
        if self.main_screen_widget:
            try:
                self.main_screen_widget.stop()
            except Exception as err:
                logger.error(f'Unable to stop screen: {err} | {pg_widget}')
            self.main_screen_container.removeWidget(self.main_screen_widget)
            logger.debug(
                f'Removed existing widget: {self.main_screen_container}')

        # Put a new one
        self.main_screen_widget = pg_widget
        self.main_screen_container.addWidget(pg_widget)
        logger.debug(f'Put {pg_widget} to {self.main_screen_container}')

    def stop_timer_and_get_timer(self):
        '''
        Stop existing timer and return a new one, which is not started
        '''
        # If exists, stop it
        if self.timer:
            self.timer.stop()
            logger.debug(f'Stopped current timer')
        # Create a new timer and return
        self.timer = QtCore.QTimer()
        return self.timer

    def _set_window_title(self, title: str = None):
        '''
        Set the title of the window
        '''
        if title is not None:
            self.window_title = title
        self.window.setWindowTitle(self.window_title)
        logger.debug(f'Set window title: {self.window_title}')
        return

    def _search_children(self):
        """
        Searches for children elements within the window object that have object names starting with 'zcc_'.

        Returns:
            dict: A dictionary containing children elements with keys as object names starting with 'zcc_'.
        """

        raw = list(self.window.findChildren(
            QtCore.QObject,
            options=QtCore.Qt.FindChildrenRecursively
        ))
        children = {
            e.objectName(): e for e in raw
            if e.objectName().startswith(self.known_component_prefix)
        }
        self.children = children
        logger.debug(f'Found children: {children}')
        return children

    def _assign_children(self):
        '''
        Link the widgets and their names
        '''
        for k, v in self.children.items():
            # Get the attribute name by removing the known component prefix
            attr = k[len(self.known_component_prefix):]

            # Warning if the subclass does not have the attribute
            # ! Disabling it since the project does not require the subclass to do so
            if False and not hasattr(self, attr):
                logger.warning(
                    f'Unknown attribute (UI has it, but window does not.): {attr}')

            # Bind the attribute to the widget
            self.__setattr__(attr, v)
            logger.debug(f'Assigned child: {attr} = {v}')
        return

    def show(self):
        """
        Shows the window object.
        """

        self.window.show()
        return

# %% ---- 2024-07-09 ------------------------
# Play ground


# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
