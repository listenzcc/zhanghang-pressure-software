"""
File: performance_ruler.py
Author: Chuncheng Zhang
Date: 2024-07-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Metrics for the computation performance with graphic ability.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-07-09 ------------------------
# Requirements and constants
import time
import numpy as np
import matplotlib as mpl

from scipy.signal import convolve2d

import threading
from threading import Thread

from .. import logger


# %% ---- 2024-07-09 ------------------------
# Function and class
class PerformanceRuler(object):
    width = 160
    height = 90
    radius = int(np.min([width, height]) / 20)
    n_types = 4
    running = False

    population = None
    unique = None
    score_buffer = None

    lock = threading.RLock()
    colormap = (
        np.array(mpl.color_sequences['tab10']) * 255).astype(np.uint8)

    threads = []

    def __init__(self):
        pass

    def init_population(self):
        '''
        Initialize the population with n_types and size of (width x height)
        '''
        # Generate population distribution map
        self.population = np.random.randint(
            low=0,
            high=self.n_types,
            size=(self.width, self.height))
        self.unique = np.unique(self.population)

        # Generate kernel for convolve2d for computing happiness
        d = self.radius * 2 + 1
        x, y = np.meshgrid(np.arange(d), np.arange(d))
        x = x - self.radius
        y = y - self.radius
        self.kernel = np.exp(-np.sqrt(x*x+y*y))
        self.kernel[self.radius, self.radius] = 0
        self.kernel /= np.sum(self.kernel)

        # Prepare score_buffer
        self.score_buffer = []
        logger.debug('Initialized population')

    def start_update(self):
        '''
        Start the updating computation
        '''
        # ! Will not start the self._update running if it is running.
        if (len(self.threads) > 0):
            logger.error(
                'Can not start update since it had not been stopped yet')
            return
        t = Thread(target=self._update, daemon=True)
        t.start()
        self.threads.append(t)

    def stop_update(self):
        '''
        Stop the updating computation.
        It waits until the thread is really terminated.
        '''
        if self.threads:
            # Stop the running
            self.running = False
            logger.debug('Sent stopping trigger')
            # Wait until the thread is really stopped
            t = self.threads.pop()
            t.join()
            logger.debug(f'Totally stopped {t}')
        return

    def _update(self):
        '''
        Update the population.
        The pixels are marked as values, each pixel is unhappy if its neighbors are of different values.
        The neighbors are located as the convolve2d with the self.kernel.
        So, the unhappy pixels exchange with each other.
        '''
        tic = time.time()
        frame_count = 0
        logger.debug('Start updating')
        self.running = True
        while self.running:
            # ----------------------------------------
            # ---- Find and move ----
            # Fill the happiness matrix which has the same size with the population matrix
            # Its values are of (0, 1), 1 refers happy, 0 refers unhappy

            # moving_array = []
            with self.lock:
                p = self.population.copy()

            happiness = np.zeros(p.shape)
            for i in self.unique:
                m = (p == i).astype(np.float32)
                h = convolve2d(m, self.kernel, mode='same')
                happiness[m == 1] = h[m == 1]

            # Compute score
            frame_count += 1
            score = np.mean(happiness)
            passed = time.time() - tic
            fps = frame_count / passed

            if frame_count % 100 == 0:
                print(
                    f'fps: {fps:0.2f}, score: {score:0.4f}, moving: {len(m)}, passed: {passed:0.2f}')

            # Find willing to moving if their happiness are low,
            # and move them.
            threshold = 0.4
            m = np.argwhere(happiness < threshold)

            # Writing stuff
            # ! The score_buffer's columns are ['passed', 'score', 'fps', 'frame_count']
            values = p[m[:, 0], m[:, 1]]
            np.random.shuffle(values)
            with self.lock:
                self.population[m[:, 0], m[:, 1]] = values
                self.score_buffer.append((passed, score, fps, frame_count))

            # Sleep to prevent blocking the system
            time.sleep(0.01)
        logger.debug('Stopped updating')
        return

    def get_quick_shot(self):
        '''
        Read the quick shot of the current stage
        Generate mat and scores:

        - mat: The RGB image of (width x height x 3).
        - scores: The scores on times.
        '''
        mat = np.zeros((self.width, self.height, 3))
        with self.lock:
            n = len(self.colormap)
            for i in self.unique:
                mat[self.population == i] = self.colormap[i % n]
            scores = np.array(self.score_buffer)
        return mat, scores


# %% ---- 2024-07-09 ------------------------
# Play ground


# %% ---- 2024-07-09 ------------------------
# Pending


# %% ---- 2024-07-09 ------------------------
# Pending
