import pandas as pd
import numpy as np

def normalize(spectra_df: pd.DataFrame, method: str = 'PQN') -> pd.DataFrame:
    """
    Apply different normalization methods to a DataFrame of spectra.

    This function normalizes the spectra in the provided DataFrame using the specified method. 
    Each row in the DataFrame represents a sample, and each column corresponds to a data point in the spectrum.

    :param spectra_df: The DataFrame containing the spectra, with samples as rows and data points as columns.
    :type spectra_df: pd.DataFrame
    :param method: The normalization method to apply. Options are 'PQN' (Probabilistic Quotient Normalization), 
        'TotalArea' (Total Area Normalization), or 'SNV' (Standard Normal Variate). Default is 'PQN'.
    :type method: str
    
    :return: The normalized spectra as a DataFrame.
    :rtype: pd.DataFrame
    """

    if method == 'PQN':
        # Probabilistic Quotient Normalization (PQN)

        # Step 1: Reference Spectrum Creation
        # Calculating the median spectrum across all samples to get the reference spectrum
        reference_spectrum = spectra_df.median(axis=0)

        # Step 2: Quotient Calculation
        # Calculating the quotients by dividing each spectrum by the reference spectrum
        quotients = spectra_df.divide(reference_spectrum, axis=1)

        # Step 3: Median Quotient Computation
        # Calculating the median quotient for each spectrum to get the scaling factors
        scaling_factors = quotients.median(axis=1)

        # Ensuring the scaling_factors are not zero to avoid division by zero errors
        scaling_factors.replace(0, 1, inplace=True)

        # Step 4: Normalization
        # Normalizing each spectrum by its respective scaling factor
        normalized_spectra = spectra_df.divide(scaling_factors, axis=0)

    elif method == 'TotalArea':
        # Total Area Normalization

        # Calculate the total area under the curve for each spectrum
        total_area = spectra_df.sum(axis=1)

        # Normalize each spectrum by dividing by the total area
        normalized_spectra = spectra_df.divide(total_area, axis=0)
        
    elif method == 'SNV':
        # Standard Normal Variate (SNV)

        # Centering each spectrum
        centered_spectra = spectra_df.subtract(spectra_df.mean(axis=1), axis=0)

        # Dividing each spectrum by the standard deviation
        std_dev = centered_spectra.std(axis=1)
        normalized_spectra = centered_spectra.divide(std_dev, axis=0)
    else:
        raise ValueError("Invalid normalization method. Choose from 'PQN', 'TotalArea', 'ReferenceCompound', 'SNV'.")

    return normalized_spectra