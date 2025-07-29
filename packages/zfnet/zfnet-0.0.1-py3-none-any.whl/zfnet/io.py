import numpy as np
import xarray as xr
from skimage.measure import points_in_poly
import os

def read_zarr(zarr_path):
    ds_zarr = xr.open_zarr(zarr_path)

    return ds_zarr

def extract_activity(ds_zarr, prefix = "", snr = 1.5):
    contour = ds_zarr[prefix+"contour"].data.compute()
    centers =  ds_zarr[prefix+"Centers"].data.compute()
    contour_boolean = []
    for z in np.unique(contour[:, -1]):
    
        z_contour = contour[contour[:, -1] == z][:, :2]
        z_centers = centers[centers[:, -1] == z][:, :2]
        contour_boolean.append(points_in_poly(z_centers, z_contour))
    
    contour_boolean = np.concatenate(contour_boolean)

    snr_boolean = ds_zarr[prefix+"SNR"].data.compute() > 1.5
    quality_boolean = contour_boolean & snr_boolean

    c = ds_zarr["C"][quality_boolean]
    norm_c = (c - np.mean(c, axis=1)) / np.std(c, axis=1)

    return norm_c, quality_boolean


