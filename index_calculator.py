import numpy as np
from typing import Dict, Any, Tuple


class GISIndexCalculator:
    """Computes spectral and SAR backscatter indices for evidence grounding."""

    @staticmethod
    def compute_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        """Normalized Difference Vegetation Index: (NIR - Red) / (NIR + Red)"""
        denom = (nir_band + red_band)
        denom[denom == 0] = 1e-5
        return (nir_band - red_band) / denom

    @staticmethod
    def compute_ndwi(green_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        """Normalized Difference Water Index: (Green - NIR) / (Green + NIR)"""
        denom = (green_band + nir_band)
        denom[denom == 0] = 1e-5
        return (green_band - nir_band) / denom

    @staticmethod
    def compute_ndbi(swir_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        """Normalized Difference Built-up Index: (SWIR - NIR) / (SWIR + NIR)"""
        denom = (swir_band + nir_band)
        denom[denom == 0] = 1e-5
        return (swir_band - nir_band) / denom

    @staticmethod
    def compute_sar_backscatter_ratio(vv_band: np.ndarray, vh_band: np.ndarray) -> np.ndarray:
        """SAR Polarization Ratio: VV / VH"""
        vh_copy = np.copy(vh_band)
        vh_copy[vh_copy == 0] = 1e-5
        return vv_band / vh_copy
