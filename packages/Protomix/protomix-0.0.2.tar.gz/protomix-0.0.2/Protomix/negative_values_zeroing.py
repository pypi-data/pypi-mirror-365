import pandas as pd

def negative_values_zeroing(spectra_df: pd.DataFrame) -> pd.DataFrame:
    """
    Set all negative values in the spectra to zero.

    This function processes a DataFrame of spectra, setting any negative values to zero while retaining
    the original structure and indexes of the DataFrame.

    :param spectra_df: A DataFrame where each row represents a spectrum, and columns correspond to spectral data points.
    :type spectra_df: pd.DataFrame
    
    :return: A DataFrame with the same structure as the input, but with all negative values replaced by zero.
    :rtype: pd.DataFrame
    """
    
    # Apply the zeroing operation to each row in the DataFrame
    corrected_spectra = spectra_df.apply(lambda spectrum: spectrum.where(spectrum >= 0, 0), axis=1)
    
    return corrected_spectra