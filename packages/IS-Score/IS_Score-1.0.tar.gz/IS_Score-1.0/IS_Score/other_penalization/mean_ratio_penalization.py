import numpy as np
from scipy import signal
from IS_Score.utils import normalizeSpectraBaseline, DebugCollector

def getMeanDipsRatioPenalization(sp: np.array, baseline: np.array):
    """
    Return the Mean Dips Ratio penalization.

    Parameters
    ----------
    sp : np.array
        The Raman spectrum.
    baseline: np.array
        The baseline spectrum.

    Returns
    -------
    mean_ratio_penalty: float
        The Mean Ratio Dips penalty.
    """
    diffGreaterDips, ratioList = [], []
    mean_ratio_penalty = 0

    for wl in [8, 16, 32, 40]:
        sp_den = signal.savgol_filter(sp, window_length=wl, polyorder=4)
        neg_sp_norm = (-sp_den - min(-sp_den)) / (max(-sp_den) - min(-sp_den))

        dips, _ = signal.find_peaks(neg_sp_norm, prominence=(None, None))
        dips = np.array(dips)

        sp_den_data, baseline_norm = normalizeSpectraBaseline(sp_den, baseline)

        # Retrieve the dips which are lower than the baseline and greater than the baseline
        index_dips_lower = dips[np.where(baseline_norm[dips] < sp_den_data[dips])[0]]
        index_dips_greater = dips[np.where(baseline_norm[dips] > sp_den_data[dips])[0]]

        if len(index_dips_greater) > 0:
            ratioList.append(len(index_dips_lower) / len(index_dips_greater))

        # Compute the difference between the dips greater than the baseline. They will be used as penalization
        diffs = baseline_norm[index_dips_greater] - sp_den_data[index_dips_greater]
        if len(diffs) > 0:
            diffGreaterDips.append(np.mean(diffs))

    if DebugCollector.enabled:
        DebugCollector.log("MEAN_RATIO_PENALIZATION", "mean_ratio_penalty", 0)

    if np.mean(ratioList) < 5:
        if DebugCollector.enabled:
            DebugCollector.log("MEAN_RATIO_PENALIZATION", "mean_ratio_penalty", np.sum(diffGreaterDips))
        mean_ratio_penalty = np.sum(diffGreaterDips)
    return mean_ratio_penalty
