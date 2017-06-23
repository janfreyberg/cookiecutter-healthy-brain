from pathlib import Path
import os
import numpy as np
import mne
import pandas as pd

# get the data path
from data import datafolder
# get the list function
import data.eeg
from functools import partial


ftype = 'preprocessed'
tasktype = 'RestingState'


# implement the raw data structures as a generator
# so that the code isn't run >400x just on import
# make the generators partial functions
def raws(**kwargs):
    for raw in data.eeg.raws(ftype, tasktype, **kwargs):
        if len(raw) > 1:
            yield raw
        elif len(raw) == 1:
            yield raw[0]


# make a generator for the events, read from file
def events():
    for event in data.eeg.events(ftype, tasktype):
        if len(raw) > 1:
            yield event
        elif len(raw) == 1:
            yield event[0]


# epochs
epochs = partial(data.eeg.epochs, ftype, tasktype)
