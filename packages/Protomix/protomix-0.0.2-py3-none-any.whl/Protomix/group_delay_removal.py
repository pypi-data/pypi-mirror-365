import pandas as pd

def group_delay_removal(fid_df: pd.DataFrame, acqus_df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove the group delay from the input FID (Free Induction Decay) data.

    This function processes the FID data by removing the group delay, which is an artifact
    introduced during data acquisition, to produce cleaner, more accurate signals.

    :param fid_df: A DataFrame where each row represents an individual FID signal, and columns represent time points.
    :type fid_df: pd.DataFrame
    :param acqus_df: A DataFrame containing acquisition parameters used to correct the group delay.
    :type acqus_df: pd.DataFrame
    
    :return: A DataFrame with the group delay removed from the FID signals.
    :rtype: pd.DataFrame
    """

    grpdly = int(acqus_df['$GRPDLY'][0])

    # Use DataFrame slicing to remove the group delay
    return fid_df.iloc[:, grpdly:]