import numpy as np
import pandas as pd

def zero_filling(fid_df: pd.DataFrame, acqus_df: pd.DataFrame, target_points: int = 5000) -> pd.DataFrame:
    """
    Zero-fill FID signals in a DataFrame to achieve the target number of points.

    This function adds zeros to the end of each FID signal in the provided DataFrame until the specified 
    target number of points is reached. Zero-filling is commonly used to increase the resolution of the 
    Fourier-transformed spectra.

    :param fid_df: A DataFrame containing FID signals, with each row representing an individual FID signal.
    :type fid_df: pd.DataFrame
    :param acqus_df: A DataFrame containing acquisition parameters relevant to the FID signals.
    :type acqus_df: pd.DataFrame
    :param target_points: The target number of points for each FID signal after zero-filling. Default is 5000.
    :type target_points: int
    
    :return: A DataFrame with FID signals that have been zero-filled to the specified target number of points.
    :rtype: pd.DataFrame
    """

    dwell_time = 1 / float(acqus_df['$SW_h'][0])
    current_points = fid_df.shape[1]
    total_points = current_points + target_points
    time_values = np.linspace(dwell_time, total_points * dwell_time, total_points)

    # Create a DataFrame of zeros with the new time values
    zero_fill_df = pd.DataFrame(0, index=fid_df.index, columns=time_values)

    # Concatenate the original DataFrame with the zero-filled DataFrame
    result_df = pd.concat([fid_df, zero_fill_df], axis=1)

    return result_df