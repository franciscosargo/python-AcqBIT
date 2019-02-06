import numpy as np

def support_metrics(array):
    Mx = array.max(axis=0)
    mx = array.min(axis=0)
    mean = np.mean(array, axis=0)
    mean_x2 = np.mean(array, axis=0)**2
    sd = np.std(array, axis=0)
    return np.stack((Mx, mx, mean, mean_x2, sd))


def _compute_support(level, ndsignal):
    n = ndsignal.shape[0]
    N = n/level
    data = ndsignal[:, 1:]
    list_split = np.array_split(data, N)
    support = np.array(map(support_metrics, list_split), copy=False)
    return support


def compute_support(ndsignal):
    return [_compute_support(level, ndsignal) for level in [10, 100, 1000]]