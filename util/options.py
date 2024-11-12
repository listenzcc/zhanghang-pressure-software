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


import contextlib
# %% ---- 2024-07-09 ------------------------
# Requirements and constants
from threading import Thread

from .feedback_mode_enum import FeedbackModeEnum
from . import logger, project_name, software_version, project_root


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
    # Main window object
    _mw = None

    # Basic info
    project_name = project_name
    version = software_version
    project_root = project_root

    # Load UI
    ui_path = project_root.joinpath('layout/main.ui')
    known_components_prefix = 'zcc_'

    # Subject info
    subjectName = '被试姓名'
    subjectAge = -1
    subjectGender = '不详'
    # datetime fmt: '%Y-%m-%d-%H-%M-%S'
    subjectExperimentDateTime = '1984-01-01-12-34-56'
    subjectRem = '其他信息'

    # Pressure options
    yMin = 0  # g
    yMax = 800  # g
    yReference = 400  # g

    # Display options
    feedbackCurveWidth = 2  # pixels
    feedbackCurveColor = '#0000a0'
    flagDisplayFeedbackCurve = True

    referenceCurveWidth = 2  # pixels
    referenceCurveColor = '#00a000'
    flagDisplayReferenceCurve = True

    delayedCurveWidth = 2  # pixels
    delayedCurveColor = '#a00000'
    delayedLength = 5  # seconds
    updateStepLength = 5  # seconds

    flagDisplayDelayedCurve = True

    flagDisplayGrid = False
    flagDisplayAxis = True
    flagDisplayMarker = True

    # Feedback model
    feedback_model: FeedbackModeEnum = None

    # Animation thresholds
    thresholdOfMean = 20  # g
    thresholdOfStd = 10  # g

    # Block design
    blockLength = 10  # seconds
    design = {"name": "N.A.", "maker": "N.A.", "_buffer": []}

    # Metrics settings
    metricThreshold1 = 0
    metricThreshold1_2 = 60
    metricThreshold2 = 60
    metricThreshold2_2 = 80
    metricThreshold3 = 80
    metricThreshold3_2 = 100

    # Metric range prompt
    metricRange1Prompt = '区间1的提示词，详见/asset/prompts/metric range1 prompt.txt'
    metricRange2Prompt = '区间2的提示词，详见/asset/prompts/metric range2 prompt.txt'
    metricRange3Prompt = '区间3的提示词，详见/asset/prompts/metric range3 prompt.txt'

    # Device settings
    idealSamplingRate = 125  # Hz
    # ! Device name, ask the product if the device changes
    productString = 'HIDtoUART example'

    # Corrections settings
    g0 = int(open(project_root.joinpath('correction/g0')).read())
    g200 = int(open(project_root.joinpath('correction/g200')).read())
    offsetG0 = int(open(project_root.joinpath('correction/offset_g0')).read())

    # Pseudo setting
    fake_file_path = None

    # Education mode flag
    education_mode_flag = False

    def write_correction(self, name, num):
        def _write():
            dst = project_root.joinpath('correction', name)
            with open(dst, 'w') as f:
                f.write(f'{num}')
            logger.debug(f'Write {num} to {dst}')
        Thread(target=_write, daemon=True).start()

    def read_metric_ranges_prompt(self):
        folder = project_root.joinpath('asset/prompts')
        with contextlib.suppress(Exception):
            self.metricRange1Prompt = open(folder.joinpath(
                'metric range1 prompt.txt'), 'r', encoding='utf8').read().strip()
        with contextlib.suppress(Exception):
            self.metricRange2Prompt = open(folder.joinpath(
                'metric range2 prompt.txt'), 'r', encoding='utf8').read().strip()
        with contextlib.suppress(Exception):
            self.metricRange3Prompt = open(folder.joinpath(
                'metric range3 prompt.txt'), 'r', encoding='utf8').read().strip()
        logger.debug('Read metric ranges prompt: {}'.format([
            self.metricRange1Prompt,
            self.metricRange2Prompt,
            self.metricRange3Prompt,
        ]))


# ! It is designed to be the singleton object,
# ! if something weird happens, check this.
rop = RunningOptions()
rop.read_metric_ranges_prompt()

# %% ---- 2024-07-09 ------------------------
# Play ground


# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
