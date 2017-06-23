from pathlib import Path
import os
import numpy as np
import mne
import pandas as pd

# get the data path (not sure this works)
from data import datafolder
# get the list function

import data.eeg
from functools import partial

ftype = 'preprocessed'
tasktype = 'Video'


# make the generators partial functions
def raws():
    for raw in data.eeg.raws(ftype, tasktype):
        if len(raw) > 1:
            yield raw
        elif len(raw) == 1:
            yield raw[0]


def events():
    for event in data.eeg.events(ftype, tasktype):
        if len(raw) > 1:
            yield event
        elif len(raw) == 1:
            yield event[0]


# for the epochs, make a slightly more elaborate function that
# fixes the event types and the duration
def epochs(**kwargs):

    for rawlist, eventlist in zip(
            data.eeg.raws(ftype, tasktype),
            data.eeg.events(ftype, tasktype)):
        pid = rawlist[0].info['subject_info']
        epochlist = []
        for raw, event in zip(rawlist, eventlist):
            duration = ((event[0, (event[:, 2] > 100) & (event[:, 2] < 110)] -
                         event[0, (event[:, 2] > 80) & (event[:, 2] < 90)]) /
                        raw.info['sfreq'])[0]

            epochlist.append(mne.Epochs(raw, event, event_id=[81, 82, 83, 84],
                                        tmax=duration, on_missing='ignore',
                                        **kwargs))

        yield mne.concatenate_epochs(epochlist)
