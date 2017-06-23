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

ftype = 'raw'
tasktype = 'SurroundSupp'


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
# fixes the event types
def epochs(**kwargs):

    for epoch in data.eeg.epochs(ftype, tasktype, event_id=8, reject=None,
                                 **kwargs):
        pid = epoch.info['subject_info']
        stimulation = pd.concat((
            pd.read_csv(f) for f in
            sorted(datafolder.glob(
                pattern=f'{pid}/Behavioral/csv_format/*{tasktype}*.csv'))))
        eventcode = np.array([cntcon * 100 + bgcon
                              for cntcon, bgcon in
                              zip(stimulation['CNTcon'], stimulation['BGcon'])])

        # insert the event codes into the epoch
        epoch.events[:, -1] = eventcode[:epoch.events.shape[0]]

        yield epoch
