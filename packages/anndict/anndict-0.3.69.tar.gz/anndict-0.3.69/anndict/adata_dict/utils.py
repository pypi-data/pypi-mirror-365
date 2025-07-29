"""
Utils for adata_dict manipulation.
"""

from anndata import AnnData

def check_and_create_stratifier(
    adata: AnnData,
    strata_keys: list[str]
    ) -> str:
    """
    Checks if the specified stratifying variables are present in the :class:`AnnData` object,
    and creates a new column combining these variables if it does not already exist.

    Parameters
    -----------
    adata
        An :class:`AnnData` object.

    strata_keys
        List of keys (column names) in ``adata.obs`` to be used for stratification.

    Returns
    ---------
    The name of the newly created or verified existing combined strata column.

    Raises
    --------
    ValueError
        If strata_keys is an empty list.

    ValueError
        If one or more of the specified stratifying variables do not exist in adata.obs.
    """
    #Check if strata_keys is an empty list
    if not strata_keys:
        raise ValueError("You specified strata_keys as an empty list. You must specify at least one stratifying variable")

    # Check if any of the strata_keys are not present in adata.obs
    if any(key not in adata.obs.columns for key in strata_keys):
        raise ValueError("one or more of your stratifying variables does not exist in adata.obs")

    # Create a new column that combines the values of existing strata_keys, if not already present
    strata_key = '_'.join(strata_keys)
    if strata_key not in adata.obs.columns:
        adata.obs[strata_key] = adata.obs[strata_keys].astype(str).agg('_'.join, axis=1).astype('category')
    else:
        #make sure it's categorical
        adata.obs[strata_key] = adata.obs[strata_key].astype('category')

    return strata_key
