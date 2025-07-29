import pandas as pd 

def region_removal(spectra_df: pd.DataFrame, range=(4.5, 6.1)) -> pd.DataFrame:
    """
    Zero out a specified ppm range in each spectrum within the DataFrame.

    This function sets the values within a specified ppm range to zero for each spectrum in the DataFrame, effectively removing that region from the spectra.

    :param spectra_df: A DataFrame where each row represents a spectrum and columns correspond to ppm values.
    :type spectra_df: pd.DataFrame
    :param range: A tuple specifying the start and end ppm values of the region to be zeroed out. Default is (4.5, 6.1).
    :type range: tuple
    
    :return: An updated DataFrame with the specified ppm range zeroed out, retaining the original indexes.
    :rtype: pd.DataFrame
    """
    
    start_ppm, end_ppm = range
    
    # Extract the columns (ppm values) within the specified range
    cols_to_zero = [col for col in spectra_df.columns if start_ppm <= float(col) <= end_ppm]
    
    # Set values in the specified columns to zero
    spectra_df.loc[:, cols_to_zero] = 0
    
    return spectra_df