import numpy as np

def _compute_support(level, ndsignal, n, p):
    N = n/level
    ndarray = ndsignal.reshape(N, level, p)
    Mx = ndarray.max(axis=1)
    mx = ndarray.min(axis=1)
    mean = np.mean(ndarray, axis=1)
    mean_x2 = np.mean(ndarray, axis=1)**2
    sd = np.std(ndarray, axis=1)
    t = list(xrange(0, n, level))
    return [Mx, mx, mean, mean_x2, sd, t]


def compute_support(ndsignal):
    ndsignal = ndsignal
    n = ndsignal.shape[0]
    p = ndsignal.shape[1]
    return [_compute_support(level, ndsignal, n, p) for level in [10, 100, 1000]]