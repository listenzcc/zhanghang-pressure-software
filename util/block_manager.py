"""
File: block_manager.py
Author: Chuncheng Zhang
Date: 2024-07-10
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Provide complex blocks manager operations.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-10 ------------------------
# Requirements and constants
from . import logger


# %% ---- 2024-07-10 ------------------------
# Function and class
class BlockManager(object):
    blocks = None
    total = 0
    empty_design_flag = False

    mark_map = {
        "Real": "T",
        "Fake": "F",
        "Hide": "+"
    }

    def __init__(self, design: dict):
        self.load_design(design)
        logger.info(f'Initialized design {design}')

    def load_design(self, design: dict):
        # Set empty_design_flag if the design contains no blocks
        if len(design['_buffer']) == 0:
            self.empty_design_flag = True
            logger.warning(
                'Using empty design, the experiment will NOT be stopped by itself')
            return

        # Parse the design to generate the offset of each blocks
        self.blocks = []
        offset = 0
        for name, duration in design['_buffer']:
            self.blocks.append(dict(
                name=name,
                start=offset,
                stop=offset+duration
            ))
            offset += duration
        self.total = offset
        logger.debug(f'Generated blocks: {self.blocks}')

    def consume(self, t):
        '''
        Consume the block on time t (seconds).

        Args:
            - t: the passed time in seconds.

        Return:
            - mark (str): notion for the block name, O for empty design, T for real feedback, F for fake feedback, + for hide feedback
            - t1 (float): remain times for the current block, -1 for empty design, 0 for running out all the blocks.
            - t2 (float): remain times for the whole experiment, -1 for empty design, 0 for running out all the blocks.
            - remain_ratio (float): percent, how many percent the experiment is remaining.
        '''
        prompts = dict(
            block_empty='Block empty'
        )
        # Return for empty design
        if self.empty_design_flag:
            return 'O', -1, -1, 1

        # Return for no blocks remained
        if len(self.blocks) == 0:
            logger.warning('No blocks remain')
            return prompts['block_empty'], 0, 0, 0

        # The blocks is not started yet
        if t < self.blocks[0]['start']:
            return 'N', self.blocks[0]["start"] - t, self.total - t

        # Consume all the passed blocks
        while t > self.blocks[0]['stop']:
            # Drop the passed blocks
            d = self.blocks.pop(0)
            logger.debug(f'Dropped passed block {d}')
            # Break if there is no block left
            if len(self.blocks) == 0:
                break

        # Again, return for no blocks remained
        if len(self.blocks) == 0:
            logger.warning('No blocks remain')
            return prompts['block_empty'], 0, 0, 0

        mark = self.mark_map.get(self.blocks[0]['name'], '?')
        t1 = self.blocks[0]['stop'] - t
        t2 = self.total - t
        remain_ratio = t2 / self.total
        return mark, t1, t2, remain_ratio


# %% ---- 2024-07-10 ------------------------
# Play ground


# %% ---- 2024-07-10 ------------------------
# Pending


# %% ---- 2024-07-10 ------------------------
# Pending
