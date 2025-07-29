import numpy as np
import pandas as pd

from scipy.optimize import minimize_scalar

def phase_correction(spectra_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply phase correction to spectra in a DataFrame.

    This function applies a phase correction to each spectrum in the provided DataFrame, ensuring that the
    spectral peaks are properly aligned.

    :param spectra_df: A DataFrame containing spectra, with each row representing a spectrum and columns corresponding to ppm values.
    :type spectra_df: pd.DataFrame
    
    :return: A DataFrame containing the phase-corrected spectra.
    :rtype: pd.DataFrame
    """

    ppm = spectra_df.columns.values

    def rms(ang, y):
        """Calculate RMS error."""
        roty = y * np.exp(1j * ang)
        Rey = np.real(roty)
        ReyPos = Rey[Rey >= 0] 
        POSss = np.sum(ReyPos ** 2)
        ss = np.sum(Rey ** 2)
        return -POSss / ss
    
    def optimize_phase_correction(spectra):
        """Optimize phase correction for multiple spectra."""
        spectra_n = spectra[:, (ppm <= 4.5) | (ppm >= 5.1)]
        f0 = rms(0, spectra_n)
        fpi = rms(np.pi, spectra_n)
        interval = (-np.pi, np.pi) if f0 < fpi else (0, 2 * np.pi)
        angles = np.empty(spectra.shape[0])
        for i, spectrum in enumerate(spectra_n):
            res = minimize_scalar(rms, args=(spectrum,), bounds=interval, method='bounded')
            angles[i] = res.x
        return spectra * np.exp(1j * angles[:, np.newaxis])
    
    spectra_values = spectra_df.to_numpy()
    corrected_spectra_values = optimize_phase_correction(spectra_values)
    
    result_df = pd.DataFrame(corrected_spectra_values, columns=ppm, index=spectra_df.index)
    return result_df