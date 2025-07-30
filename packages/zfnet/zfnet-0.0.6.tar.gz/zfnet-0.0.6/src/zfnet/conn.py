from scipy.signal import find_peaks
import numpy as np
import tqdm
from numba import njit, prange, jit

def find_peaks_in_signal(norm_c, prominence = 0.05):
    binary_peaks = []
    
    for neuron in range(norm_c.shape[0]):
        binary = np.zeros(norm_c.shape[1])
        peaks = find_peaks(norm_c[neuron].values, prominence=prominence)
        if len(peaks[0]) > 0:
            binary[peaks[0]] = 1
        binary_peaks.append(binary)
    peak_data = np.stack(binary_peaks).astype("float32")   

    return peak_data

@njit(parallel = True)
def compute_correlation(data, window= 20):
    N = data.shape[0]
    T = data.shape[1]
    K = data.shape[1]//window
    results = np.zeros((N, N, K), dtype = "int8")
    lags = np.arange(-window + 1, window)

    for k in prange(K):
        
        for i in range(N):
            for j in range(N):
                a = data[i, k * window : (k+1) * window]
                v = data[j, k * window : (k+1) * window]
                #a = (a - np.mean(a)) / np.std(a)
                #v = (v - np.mean(v)) / np.std(v)
                corr = np.correlate(a, v, mode='full')

                a_max = np.max(a)
                idx = np.argmax(corr)
                max_corr = corr[idx]
                lag = lags[idx]
                
                if (max_corr > 0.3) & (lag > 0) & (a_max == 1):
                    conn = 1 # directed forward connection
                else:   
                    conn = 0 # no connection
                results[i, j, k] = conn
    return results