"""
File: options.py
Author: Chuncheng Zhang
Date: 2024-07-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Options for the project

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-09 ------------------------
# Requirements and constants
from . import project_name, software_version, project_root


# %% ---- 2024-07-09 ------------------------
# Function and class
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RunningOptions(object, metaclass=Singleton):
    # Basic info
    project_name = project_name
    version = software_version
    project_root = project_root

    # Load UI
    ui_path = project_root.joinpath('layout/main.ui')
    known_components_prefix = 'zcc_'

    # Pressure options
    yMin = 0
    yMax = 400
    yReference = 200

    # Display options
    feedbackCurveWidth = 2
    feedbackCurveColor = '#0000a0'

    referenceCurveWidth = 2
    referenceCurveColor = '#00a000'
    flagDisplayReferenceCurve = True

    delayedCurveWidth = 2
    delayedCurveColor = '#a00000'
    delayedLength = 5
    updateStepLength = 5

    flagDisplayDelayedCurve = True

    # Animation thresholds
    thresholdOfMean = 20
    thresholdOfStd = 10

    # Block design
    blockLength = 10
    design = {"name": "N.A.", "maker": "N.A.", "_buffer": []}

    # Metrics settings
    metricThreshold1 = 30
    metricThreshold2 = 60
    metricThreshold3 = 90


# ! It is designed to be the singleton object,
# ! if something weird happens, check this.
rop = RunningOptions()

# %% ---- 2024-07-09 ------------------------
# Play ground


# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
