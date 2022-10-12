import mne
from mnelab.io.xdf import read_raw_xdf
from pyxdf import match_streaminfos, resolve_streams

def import_files(resample = True):
    raws = []
    
    for fname in ("sub-P002_ses-S001_task-Default_run-001_eeg_ME.xdf", "sub-P002_ses-S002_task-Default_run-001_eeg_ME.xdf",
                  "sub-P002_ses-S003_task-Default_run-001_eeg_ME.xdf", "sub-P003_ses-S001_task-Default_run-001_eeg_ME.xdf",
                  "sub-P003_ses-S002_task-Default_run-001_eeg_ME.xdf", "sub-P003_ses-S003_task-Default_run-001_eeg_ME.xdf", 
                  "sub-P004_ses-S001_task-Default_run-001_eeg_ME.xdf", "sub-P004_ses-S002_task-Default_run-001_eeg_ME.xdf", 
                  "sub-P004_ses-S003_task-Default_run-001_eeg_ME.xdf", "sub-P005_ses-S001_task-Default_run-001_eeg_ME.xdf", 
                  "sub-P005_ses-S002_task-Default_run-001_eeg_ME.xdf", "sub-P005_ses-S003_task-Default_run-001_eeg_ME.xdf", 
                  "sub-P006_ses-S001_task-Default_run-001_eeg_ME.xdf", "sub-P006_ses-S002_task-Default_run-001_eeg_ME.xdf",
                  "sub-P006_ses-S003_task-Default_run-001_eeg_ME.xdf"):
        
        stream_id = match_streaminfos(resolve_streams(fname), [{"type": "EEG"}])[0]
        raw_temp = read_raw_xdf (fname, stream_id=stream_id)
        
        if resample:
            raw_resampled = raw_temp.resample(500) # if applicable!
        
        raws.append(raw_resampled)

    raw = mne.concatenate_raws(raws)
    del raws

    return raw