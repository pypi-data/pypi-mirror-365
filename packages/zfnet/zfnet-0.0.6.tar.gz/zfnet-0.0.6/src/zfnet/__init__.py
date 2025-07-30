"""Top-level package for zfnet."""

__author__ = """Pierce Mullen"""
__email__ = 'pnm1@st-andrews.ac.uk'
__version__ = '0.0.6'

from .io import read_zarr, extract_activity
from .conn import find_peaks_in_signal, compute_correlation
from .visualize import visualize_graph
from .isomorphic_matching import create_motifs, nx_match_motifs, pygm_match_motifs, get_matches_from_softmatch
