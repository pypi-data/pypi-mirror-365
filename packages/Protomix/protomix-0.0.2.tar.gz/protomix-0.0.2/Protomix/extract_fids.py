import os
import numpy as np
import pandas as pd

def extract_fids(root_directory: str, acqus_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Free Induction Decay (FID) data from binary files and construct a DataFrame.

    This function navigates through a specified directory, locates binary files named 'fid',
    and extracts FID data from them. It then assembles a DataFrame where each row represents
    the complex FID signal from a sample, with columns corresponding to time points calculated
    using the dwell time from the `acqus_df` DataFrame.

    :param root_directory: The root directory path containing subdirectories with 'fid' files.
    :type root_directory: str
    :param acqus_df: A DataFrame containing acquisition parameters, specifically the 
        spectral width ('$SW_h') used for dwell time calculation.
    :type acqus_df: pd.DataFrame

    :return: A DataFrame where each row corresponds to a sample's FID data (as complex values),
        with columns representing time points.
    :rtype: pd.DataFrame

    :raises AssertionError: If `root_directory` is not a string, does not exist, is not a directory, 
        contains no 'fid' files, or if any 'fid' file has an unexpected data length.
    """

    # Check the type of root_directory
    assert isinstance(root_directory, str), "root_directory should be a string."
    
    # Check if root_directory exists and is a directory
    assert os.path.exists(root_directory) and os.path.isdir(root_directory), "root_directory should point to an existing directory."
    
    # Initialize lists to store fid data and sample names
    fid_files = []
    sample_names = []
    
    # Get paths of fid files using os.walk and list comprehension
    paths = [os.path.join(root, file) for root, _, files in os.walk(root_directory)
             for file in files if file == 'fid']
    
    # Check if paths list is not empty
    assert paths, "No 'fid' files found in the specified directory."
    
    for data_file in paths:
        sample_names.append(data_file.split(os.path.sep)[-3])
        
        # Read binary data directly into a numpy array
        binary_data = np.fromfile(data_file, dtype="int32")
        
        # Ensure that binary data is even-length
        assert len(binary_data) % 2 == 0, f"Unexpected data length in {data_file}."
        
        # Convert binary data to complex signal directly
        complex_signal = binary_data[::2] + 1j * binary_data[1::2]
        fid_files.append(complex_signal)

    # Calculate dwell time and time array once
    dwell_time = 1 / (float(acqus_df['$SW_h'][0]))
    number_of_points = len(fid_files[0])
    time = np.linspace(dwell_time, number_of_points * dwell_time, number_of_points)   

    # Create DataFrame with fid data and appropriate index and columns
    fid_df = pd.DataFrame(fid_files, index=sample_names, columns=time, dtype=np.complex128)
    
    return fid_df
