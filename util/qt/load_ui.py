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

    def __init__(self):
        self._search_children()
        self._assign_children()
        self._set_window_title()

    def _set_window_title(self, title: str = None):
        '''
        Set the title of the window
        '''
        if title is not None:
            self.window_title = title
        self.window.setWindowTitle(self.window_title)
        logger.debug(f'Set window title: {self.window_title}')

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
        logger.debug(f'Found children: {children}')
        self.children = children
        return children

    def _assign_children(self):
        '''
        Link the widgets and their names
        '''
        for k, v in self.children.items():
            attr = k[len(self.known_component_prefix):]

            if not hasattr(self, attr):
                logger.warning(
                    f'Unknown attribute (UI has it, but window does not.): {attr}')

            self.__setattr__(attr, v)

            logger.debug(f'Assigned child: {attr} = {v}')

    def show(self):
        """
        Shows the window object.

        Returns:
            None
        """

        self.window.show()

# %% ---- 2024-07-09 ------------------------
# Play ground


# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
