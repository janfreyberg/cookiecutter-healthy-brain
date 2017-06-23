## Cookiecutter template for working with the healthy brain data

This is a template that implements some nice data-import syntax for the healthy brain Child Mind Institute data.

The main benefit to using this template is the provided data imports.

#### Downloading data
---

For example, to download some data, you can use:

```python
from data.download import download_sample_eeg

download_sample_eeg(n=5)
```

This will download 5 EEG  datasets

#### Importing data
---

You can also import data by simply using an import statement:

```
from data.eeg.preprocessed.resting_state import raws

for raw in raws():
    # <your code here>
```

#### Implemented so far
---

At the moment, I've implemented raw and preprocessed EEG data imports for the resting-state, the video and the surround suppression conditions. For each one, you can import `raws` (`mne.Raw`), `epochs` (`mne.Epochs`), and `events` (nx3 `numpy.array`).

When import raw data (`from data.eeg.raw...`), you will literally just get all the data loaded in an MNE data structure. You can import the events and do the epoching yourself: `from data.eeg.raw.resting_state import events`.

So the following:

```
from data.eeg.preprocessed.resting_state import raws, events

for raw, event in zip(raws(), events():
    epoch = mne.Epochs(raw, event, tmin=0, tmax=20)
```

would be equivalent to:

```
from data.eeg.preprocessed.resting_state import epochs

for epoch in epochs(tmin=0, tmax=20):
    pass
```

The epoching is done semi-intelligently, so for example, when importing for the `video` condition, you get Epochs that start with the video start and end with the video end. Do double check each import and how epochs are defined, simply check the corresponding python scripts!

