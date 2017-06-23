import boto3
from botocore import UNSIGNED
from botocore.client import Config

from data import datafolder

import requests
import os
import random  # random sampling
from pathlib import Path  # path operations
import shutil  # unzip utils
try:
    from tqdm import tqdm_notebook as tqdm  # progress bar
except:
    from tqdm import tqdm as tqdm  # progress bar

s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

remote_eeg_files = s3.list_objects(
    Bucket='fcp-indi', Prefix='data/Projects/HBN/S1/EEG/')['Contents']
remote_mri_files = (
    s3.list_objects(Bucket='fcp-indi',
                    Prefix='data/Projects/HBN/S1/MRI/RU')['Contents'] +
    s3.list_objects(Bucket='fcp-indi',
                    Prefix='data/Projects/HBN/S1/MRI/SI')['Contents']
)

n_eeg = len(remote_eeg_files)
n_mri = len(remote_mri_files)


# EEG Files --------------------------------------------------------------------
def download_all_eeg():
    print(f"Downloading {n_eeg} EEG data sets.")
    for fileobj in tqdm(remote_eeg_files, desc='Files'):
        # request the file
        requests.get(f"https://s3.amazonaws.com/fcp-indi/{fileobj['Key']}",
                     stream=True)

        total_length = int(r.headers.get('content-length'))

        with open(datafolder / Path(fileobj['Key']).name, 'wb+') as f:
            for chunk in tqdm(r.iter_content(chunk_size=1024),
                              total=(total_length / 1024), desc='Bytes'):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)


def download_sample_eeg(n=1):
    print(f"Downloading {n} random EEG data set(s).")
    for fileobj in tqdm(random.sample(remote_eeg_files, n), desc='Files'):
        # request the file
        r = requests.get(f"http://s3.amazonaws.com/fcp-indi/{fileobj['Key']}",
                         stream=True)

        total_length = int(r.headers.get('content-length'))

        with open(datafolder / Path(fileobj['Key']).name, 'wb+') as f:
            for chunk in tqdm(r.iter_content(chunk_size=1024),
                              total=(total_length / 1024), desc='Bytes'):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)


# MRI Files --------------------------------------------------------------------
def download_sample_mri(n=1):
    print(f"Downloading {n} random MRI data set(s).")
    for fileobj in tqdm(random.sample(remote_mri_files, n), desc='Files'):
        # request the file
        r = requests.get(f"http://s3.amazonaws.com/fcp-indi/{fileobj['Key']}",
                         stream=True)

        total_length = int(r.headers.get('content-length'))

        with open(datafolder / Path(fileobj['Key']).name, 'wb+') as f:
            for chunk in tqdm(r.iter_content(chunk_size=1024),
                              total=(total_length / 1024), desc='Bytes'):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)


def download_all_mri():
    print(f"Downloading {n_mri} MRI data sets.")
    for fileobj in tqdm(remote_mri_files, desc='Files'):
        # request the file
        r = requests.get(f"http://s3.amazonaws.com/fcp-indi/{fileobj['Key']}",
                         stream=True)

        total_length = int(r.headers.get('content-length'))

        with open(datafolder / Path(fileobj['Key']).name, 'wb+') as f:
            for chunk in tqdm(r.iter_content(chunk_size=1024),
                              total=(total_length / 1024), desc='Bytes'):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)


# Extraction -------------------------------------------------------------------
def extract_all(delete_archives=True, delete_matfiles=True):
    local_archives = list(datafolder.glob(pattern='*.tar.gz'))
    print(f"Extracting {len(local_archives)} files.")
    for f in tqdm(local_archives, desc='Extracting'):
        shutil.unpack_archive(f, datafolder, 'gztar')
        if delete_archives:
            os.remove(f)
        if delete_matfiles:
            for folder in list(datafolder.glob(pattern='**/mat_format')):
                shutil.rmtree(folder)
