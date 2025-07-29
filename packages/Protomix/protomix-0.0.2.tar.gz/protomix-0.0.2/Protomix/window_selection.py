import pandas as pd

def window_selection(spectra_df: pd.DataFrame, range=(0.2, 10)) -> pd.DataFrame:
    """
    Extract a specified ppm range from the `spectra_df` DataFrame.

    This function extracts the spectral data within a specified ppm range from each spectrum in the DataFrame.
    The resulting DataFrame retains the original indexes but only includes the selected ppm range.

    :param spectra_df: A DataFrame where each row represents a spectrum and columns correspond to ppm values.
    :type spectra_df: pd.DataFrame
    :param range: A tuple specifying the start and end ppm values of the region to extract. Default is (0.2, 10).
    :type range: tuple
    
    :return: A DataFrame containing only the spectral data within the specified ppm range, retaining the original indexes.
    :rtype: pd.DataFrame
    """
    
    start_ppm, end_ppm = range
    
    # Extract the columns (ppm values) within the specified range
    cols_to_extract = [col for col in spectra_df.columns if start_ppm <= float(col) <= end_ppm]
    
    return spectra_df.loc[:, cols_to_extract]
