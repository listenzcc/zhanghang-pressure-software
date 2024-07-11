"""
File: experiment_enum.py
Author: Chuncheng Zhang
Date: 2024-07-11
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Enumerates of the feedback mode

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-11 ------------------------
# Requirements and constants
from enum import Enum


# %% ---- 2024-07-11 ------------------------
# Function and class


class FeedbackModeEnum(Enum):
    curveFeedback = 1
    holdingBallFeedback = 2
    buildingUpFeedback = 3
    catOutOceanFeedback = 4
    catClimbTreeFeedback = 5


def get_feedback_mode_info(exp):
    if exp == FeedbackModeEnum.curveFeedback:
        return '线条反馈'
    elif exp == FeedbackModeEnum.holdingBallFeedback:
        return '压力球反馈'
    elif exp == FeedbackModeEnum.buildingUpFeedback:
        return '建房子反馈'
    elif exp == FeedbackModeEnum.catOutOceanFeedback:
        return '猫与潜水艇反馈'
    elif exp == FeedbackModeEnum.catClimbTreeFeedback:
        return '猫爬树反馈'
    else:
        return

# %% ---- 2024-07-11 ------------------------
# Play ground


# %% ---- 2024-07-11 ------------------------
# Pending


# %% ---- 2024-07-11 ------------------------
# Pending
