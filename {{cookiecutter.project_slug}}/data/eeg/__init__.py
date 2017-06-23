from pathlib import Path
import os
import numpy as np
import mne
import pandas as pd

# get the data path (not sure this works)
from data import datafolder

# the types of files this dataset has
filetypes = ['chanlocs', 'event', 'data']

# make a list of the resting state files


def _get_files(ftype, tasktype):
    datafiles = sorted(datafolder.glob(
        pattern=f'*/EEG/{ftype}/csv_format/*{tasktype}*data.csv'))
    eventfiles = sorted(datafolder.glob(
        pattern=f'*/EEG/{ftype}/csv_format/*{tasktype}*event.csv'))
    # for some reason the chan loc files are ONLY in preprocessed
    chanlocfiles = sorted(datafolder.glob(
        pattern=f'*/EEG/preprocessed/csv_format/*{tasktype}*chanlocs.csv'))

    # get the IDs of every subject with this data
    pids = list(set([f.parts[-5] for f in datafiles]))

    datafiles = {pid: [f for f in datafiles if pid in f.parts]
                 for pid in pids}
    eventfiles = {pid: [f for f in eventfiles if pid in f.parts]
                  for pid in pids}
    chanlocfiles = {pid: [f for f in chanlocfiles if pid in f.parts]
                    for pid in pids}

    # number of files
    n = len(pids)

    return pids, datafiles, eventfiles, chanlocfiles, n


def raws(ftype, tasktype, **kwargs):
    # in this case, this will return a LIST of raws

    # list files
    pids, datafiles, eventfiles, chanlocfiles, n = _get_files(
        ftype, tasktype)

    for pid in pids:
        n_subject = len(datafiles[pid])

        rawlist = []
        for block in range(n_subject):
            # load the data from the text file
            with open(datafiles[pid][0], 'r') as f:
                data = np.stack([np.fromstring(line, sep=',') for line in f],
                                axis=0)

            # for some reason the chan locs are only there for
            # preprocessed files, so let's just ignore em
            if ftype == 'preprocessed':
                # read the channel locations:
                chanlocs = pd.read_csv(chanlocfiles[pid][block])
                ch_names = list(chanlocs['labels'])
                pos = np.array(chanlocs.loc[:, ('X', 'Y', 'Z')])
                # make a montage from the chanlocs
                mtg = mne.channels.Montage(pos, ch_names, 'custom',
                                           range(len(ch_names)))

            else:
                mtg = None
                ch_names = None

            # make info structure
            info = mne.create_info(ch_names=data.shape[0], sfreq=500,
                                   ch_types='eeg', montage=mtg)
            info['subject_info'] = pid

            # find bad electrodes
            if ftype == 'preprocessed':
                badbool = np.all(data == 0, axis=1)
                info['bads'] = [ch for b, ch in zip(badbool.ravel(), ch_names)
                                if b]

            # make a raw structure
            rawlist.append(mne.io.RawArray(data, info, **kwargs))

        yield rawlist


def events(ftype, tasktype):
    # list files
    pids, datafiles, eventfiles, chanlocfiles, n = _get_files(
        ftype, tasktype)
    for pid in pids:

        n_subject = len(datafiles[pid])

        # get the number of decoding files for this subject
        # stimfiles = list(datafolder.glob(
        #     pattern=f'{pid}/Behavioral/csv_format/*{tasktype}*.csv'))

        # empty lists for appending
        eventarrays = []
        for block in range(n_subject):
            # read event file
            # read the events file and the behav file
            eventdf = pd.read_csv(eventfiles[pid][block])
            # drop superfluous events
            if eventdf['type'].dtype is not np.dtype(int):
                eventdf = eventdf.loc[eventdf['type'] != 'break cnt', :]

            eventarray = np.array([eventdf.loc[:, 'sample'],
                                   np.zeros(eventdf.shape[0]),
                                   eventdf.loc[:, 'type']],
                                  dtype='int').T
            eventarrays.append(eventarray)

        yield eventarrays


# implement the epoch data structures as a generator
# so that the code isn't run >400x just on import
def epochs(ftype, tasktype, **kwargs):

    for rawlist, eventlist in \
        zip(raws(ftype, tasktype),
            events(ftype, tasktype)):

        epochlist = []
        for raw, eventarray in zip(rawlist, eventlist):
            epochlist.append(mne.Epochs(raw, eventarray,
                                        **kwargs))
        print(raw.info['subject_info'])
        # ensure the bads are the same
        bads = list(set(sum((e.info['bads'] for e in epochlist), [])))
        for epoch in epochlist:
            epoch.info['bads'] = bads

        # concatenate the two epoch structs since they are equivalent
        yield mne.concatenate_epochs(epochlist)
