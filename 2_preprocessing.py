import mne
import numpy as np

class Preprocessing_Steps():

    def preprocessing(self, raw , Filter = True, include_ICA = True):
        
        raw.drop_channels(["ACC_X", "ACC_Y", "ACC_Z"])
        raw.add_reference_channels("FCz")
        raw.set_montage("easycap-M1")
        raw.set_eeg_reference(["TP9", "TP10"])

        picks = mne.pick_types(raw.info, eeg=True, eog=False, stim=False)

        if Filter:
            # Notch filter
            raw.notch_filter(np.arange(60, 241, 60), picks=picks, filter_length='auto', phase='zero') # remove power line periodic noise
            # Bandpass filter
            raw.filter(1, 50., fir_design='firwin') # remove slow drift and consider freqs up to 50Hz

        if include_ICA:
            raw = self.ICA_process(raw) # run ICA

        return raw

    def ICA_process(self,raw):

        filt_raw = raw.copy().filter(l_freq=1., h_freq=None)
        ica = ICA(n_components=5, max_iter='auto', random_state=97)
        ica.fit(filt_raw)

        # find which ICs match the EOG pattern
        eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name ='Fp2')
        ica.exclude = eog_indices
        # print ('ica.exclude', ica.exclude)
        reconst_raw = raw.copy()
        ica.apply(reconst_raw)

        return reconst_raw