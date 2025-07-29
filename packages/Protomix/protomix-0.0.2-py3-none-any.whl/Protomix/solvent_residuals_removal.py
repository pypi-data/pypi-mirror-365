import numpy as np
import pandas as pd

from scipy.linalg import pascal
from scipy.sparse import eye, csr_matrix, csc_matrix
from scipy.sparse.linalg import splu

def solvent_residuals_removal(fid_df: pd.DataFrame, lam: float = 1e6, returnSolvent: bool = False):
    """
    Remove solvent residuals from the input FID (Free Induction Decay) data.

    This function processes the input FID data to remove solvent residuals, which are unwanted signals
    typically present in NMR data. The function can also return the solvent residuals if specified.

    :param fid_df: A DataFrame where each row represents an individual FID signal, and columns correspond to time points.
    :type fid_df: pd.DataFrame
    :param lam: The regularization parameter used during the removal process. Defaults to 1e6.
    :type lam: float
    :param returnSolvent: If True, the function returns both the corrected FID data and the solvent residuals. Defaults to False.
    :type returnSolvent: bool
    
    :return: If `returnSolvent` is False, returns a DataFrame with the corrected FID data.
             If `returnSolvent` is True, returns a tuple of two DataFrames: (corrected FID data, solvent residuals).
    :rtype: pd.DataFrame or tuple of (pd.DataFrame, pd.DataFrame)
    """
    
    def diff(m, d=2):
        """Computes the sparse differentiation matrix."""
        nums = pascal(d + 1, kind='lower')[-1].astype(float)
        minuses_from = d % 2 + 1 if d != 1 else d % 2
        nums[minuses_from::2] *= -1
        data = np.tile(nums, m - d)
        row_ind = (np.arange(d + 1) + np.arange(m - d).reshape(-1, 1)).flatten()
        col_ind = np.repeat(np.arange(m - d), d + 1)
        return csr_matrix((data, (row_ind, col_ind)), shape=(m, m - d)).T
    
    def difsm(y, d=2):
        """Computes the solvent residuals."""
        m = len(y)
        E = eye(m)
        D = diff(m, d=2)
        A = E + lam * D.T.dot(D)
        C = splu(csc_matrix(A)) # Convert to CSC format before LU decomposition
        return C.solve(C.solve(y))
    
    def apply_residual_removal(fid):
        solventRe = difsm(y=fid.real)
        solventIm = difsm(y=fid.imag)
        solvent = solventRe + 1j * solventIm
        corrected_fid = fid - solvent
        return corrected_fid, solvent

    fids, solvents = zip(*[apply_residual_removal(row.values) for _, row in fid_df.iterrows()])
    fids_df = pd.DataFrame(fids, index=fid_df.index, columns=fid_df.columns)
    solvent_df = pd.DataFrame(solvents, index=fid_df.index, columns=fid_df.columns)
        
    return (fids_df, solvent_df) if returnSolvent else fids_df