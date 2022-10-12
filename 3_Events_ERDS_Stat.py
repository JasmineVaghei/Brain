import mne
from mne.stats import permutation_cluster_1samp_test as pcluster_test

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

# used mne documentations for the following analyses                

def create_events_epochs(raw , tmin =-1, tmax =4):

    events, _ = mne.events_from_annotations(raw)

    events = events[np.in1d(events[:, 2], (2, 3, 4, 5, 6)), :]   # numbers defined in Psychopy

     
    epochs = mne.Epochs(raw, events, dict(left=2, right=3, down=4, up= 5, stop=6), tmin, tmax,    # 5-class cassification
                        picks=('F3','Fp1','Fz','Fp2','F4'), baseline=None, preload=True)          # select channels for analysis
    
    return events, epochs

def clustered_ERDS(epochs, tfr): 
    
    vmin, vmax = -1, 1.5  # set min and max ERDS values in plot
    cnorm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)  # min, center & max ERDS

    kwargs = dict(n_permutations=100, step_down_p=0.05, seed=1,
              buffer_size=None, out_type='mask')  # for cluster test
    event_ids = dict(left=2, right=3, down=4, up= 5, stop=6)

    for event in event_ids:
        # select desired epochs for visualization
        tfr_ev = tfr[event]
        fig, axes = plt.subplots(1, 4, figsize=(12, 4),
                                gridspec_kw={"width_ratios": [10, 10, 10, 1]})
        for ch, ax in enumerate(axes[:-1]):  # for each channel
            # positive clusters
            _, c1, p1, _ = pcluster_test(tfr_ev.data[:, ch], tail=1, **kwargs)
            # negative clusters
            _, c2, p2, _ = pcluster_test(tfr_ev.data[:, ch], tail=-1, **kwargs)

            # note that we keep clusters with p <= 0.05 from the combined clusters
            # of two independent tests; in this example, we do not correct for
            # these two comparisons
            c = np.stack(c1 + c2, axis=2)  # combined clusters
            p = np.concatenate((p1, p2))  # combined p-values
            mask = c[..., p <= 0.05].any(axis=-1)

            # plot TFR (ERDS map with masking)
            tfr_ev.average().plot([ch], cmap="RdBu", cnorm=cnorm, axes=ax,
                                colorbar=False, show=False, mask=mask,
                                mask_style="mask")

            ax.set_title(epochs.ch_names[ch], fontsize=10)
            ax.axvline(0, linewidth=1, color="black", linestyle=":")  # event
            if ch != 0:
                ax.set_ylabel("")
                ax.set_yticklabels("")
        fig.colorbar(axes[0].images[-1], cax=axes[-1]).ax.set_yscale("linear")
        fig.suptitle(f"ERDS ({event})")
        plt.show()
    
def confidence_map(tfr):
    df = tfr.to_data_frame(time_format=None, long_format=True)

    # Map to frequency bands:
    freq_bounds = {'_': 0,
                'delta': 3,
                'theta': 7,
                'alpha': 13,
                'beta': 35,
                'gamma': 140}
    df['band'] = pd.cut(df['freq'], list(freq_bounds.values()),
                        labels=list(freq_bounds)[1:])

    # Filter to retain only relevant frequency bands:
    # freq_bands_of_interest = ['delta', 'theta', 'alpha', 'beta']
    freq_bands_of_interest = ['theta']
    df = df[df.band.isin(freq_bands_of_interest)]
    df['band'] = df['band'].cat.remove_unused_categories()

    # Order channels for plotting:
    df['channel'] = df['channel'].cat.reorder_categories(('F3','Fp1','Fz','Fp2','F4'),
                                                        ordered=True)

    g = sns.FacetGrid(df, row='band', col='channel', margin_titles=True)
    g.map(sns.lineplot, 'time', 'value', 'condition', n_boot=10)
    axline_kw = dict(color='black', linestyle='dashed', linewidth=0.5, alpha=0.5)
    g.map(plt.axhline, y=0, **axline_kw)
    g.map(plt.axvline, x=0, **axline_kw)
    g.set(ylim=(None, 4))
    g.set_axis_labels("Time (s)", "ERDS (%)")
    g.set_titles(col_template="{col_name}", row_template="{row_name}")
    # g.add_legend(ncol=2, loc='lower center')
    g.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.08)
    plt.show()