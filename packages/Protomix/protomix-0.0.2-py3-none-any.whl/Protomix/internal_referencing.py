import numpy as np
import pandas as pd

def internal_referencing(spectra_df: pd.DataFrame, ppm_min: float = -0.2, ppm_max: float = 0.2) -> pd.DataFrame:
    """
    Reference a DataFrame of NMR spectra by shifting the spectrum values to align the TSP peak to 0 ppm.

    This function adjusts the chemical shift values in the provided NMR spectra so that the TSP (trimethylsilyl propionate) peak is set to 0 ppm. The adjustment is performed within a specified ppm range.

    :param spectra_df: A DataFrame where each row represents a complex NMR spectrum, and columns correspond to ppm (parts per million) values.
    :type spectra_df: pd.DataFrame
    :param ppm_min: The minimum ppm value for the search range to locate the TSP peak. Default is -0.2.
    :type ppm_min: float, optional
    :param ppm_max: The maximum ppm value for the search range to locate the TSP peak. Default is 0.2.
    :type ppm_max: float, optional
    
    :return: A DataFrame with spectra shifted so that the TSP peak is aligned at 0 ppm, with the original ppm values as column names.
    :rtype: pd.DataFrame
    """
    
    def apply_internal_referencing(spectrum, ppm, ppm_min=-0.2, ppm_max=0.2):
        """
        Reference a single NMR spectrum by shifting the spectrum values to set the TSP peak to 0 ppm.
        
        Parameters:
        - spectrum (numpy array): The intensity values of the spectrum.
        - ppm (numpy array): The chemical shift values corresponding to the spectrum.
        - ppm_min (float, optional): The minimum ppm value for the search range. Default is -0.2.
        - ppm_max (float, optional): The maximum ppm value for the search range. Default is 0.2.
        
        Returns:
        - tuple: The shifted spectrum and the original chemical shifts.
        """
    
        # Select the data within the specified ppm range
        search = (ppm >= ppm_min) & (ppm <= ppm_max)
        spectrum_search = spectrum[search]

        # Determine the TSP peak intensity within the ppm range
        reference_intensity = np.max(spectrum_search)
    
        # Find the index of that intensity in the full spectrum
        reference_idx_full_spectrum = np.where(spectrum == reference_intensity)[0][0]

        # Determine the index in the original ppm array where ppm is closest to 0
        target_idx = np.abs(ppm).argmin()
    
        # Calculate the number of positions to shift the spectrum values
        shift_positions = target_idx - reference_idx_full_spectrum

        # Shift the spectrum values
        spectrum_shifted = np.roll(spectrum, shift_positions)

        return spectrum_shifted, ppm
    
    # Extract ppm values from column names
    ppm = spectra_df.columns.astype(float).values
    
    # Initialize an empty DataFrame to store the results
    result_df = pd.DataFrame(columns=spectra_df.columns)
    
    for index, row in spectra_df.iterrows():
        # Take the real part of the complex spectrum
        spectrum_real = np.real(row.values)
        
        # Reference the spectrum using the internal standard
        spectrum_shifted, _ = apply_internal_referencing(spectrum_real, ppm, ppm_min, ppm_max)
        
        # Append the shifted spectrum to the result DataFrame
        result_df.loc[index] = spectrum_shifted
    
    return result_df
