"""
File: main.py
Author: Chuncheng Zhang
Date: 2024-07-08
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Main entrance

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-08 ------------------------
# Requirements and constants
from rich import print

from util import logger
from util.joint import mw, ms


# %% ---- 2024-07-08 ------------------------
# Function and class


# %% ---- 2024-07-08 ------------------------
# Play ground
if __name__ == "__main__":
    mw.window.show()

    print(mw.children)

    # Execute and exit the UI
    app = mw.app
    app.exec_()
    app.exit()


# %% ---- 2024-07-08 ------------------------
# Pending


# %% ---- 2024-07-08 ------------------------
# Pending
