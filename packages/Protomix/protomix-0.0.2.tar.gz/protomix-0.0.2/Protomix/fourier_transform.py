import numpy as np
import pandas as pd

def fourier_transform(fid_df: pd.DataFrame, acqus_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply Fourier Transform to FID (Free Induction Decay) signals in a DataFrame and convert to chemical shift values in ppm.

    This function takes a DataFrame containing rows of FID signals, applies the Fourier Transform to each row,
    and then scales the frequencies to chemical shift values in ppm using parameters from the `acqus_df` DataFrame.

    :param fid_df: DataFrame containing FID signals in rows. Each row represents an FID signal from a sample.
    :type fid_df: pd.DataFrame
    :param acqus_df: DataFrame containing acquisition parameters necessary for the transformation. 
        It should include spectral width (`$SW_h`), spectral offset (`$O1`), and NMR frequency (`$SFO1`).
    :type acqus_df: pd.DataFrame

    :return: DataFrame containing Fourier-transformed spectra. Columns represent chemical shift values in ppm,
        and rows correspond to the transformed FID signals.
    :rtype: pd.DataFrame

    :notes: The function performs a Fourier Transform on each FID signal in `fid_df`. The spectral width (`$SW_h`),
        spectral offset (`$O1`), and NMR frequency (`$SFO1`) from `acqus_df` are used to calculate the ppm scale for the spectra.
    """

    # Get the values from the DataFrame as a NumPy array
    fid_values = fid_df.values

    # Fourier transform the FIDs
    spectra = np.fft.fftshift(np.fft.fft(fid_values, axis=1), axes=1)

    # Create a frequency array corresponding to the Fourier transform
    num_points = fid_values.shape[1]
    dwell_time = 1 / (float(acqus_df['$SW_h'][0]))
    offset = float(acqus_df['$O1'][0])
    freq_nmr = float(acqus_df['$SFO1'][0])

    freq = np.fft.fftfreq(num_points, d=dwell_time)
    freq = np.fft.fftshift(freq + offset)

    # Convert the frequency to ppm using the NMR frequency
    ppm = freq / freq_nmr

    # Create a DataFrame from the spectra with ppm as the index
    result_df = pd.DataFrame(spectra, columns=ppm, index=fid_df.index)

    return result_df