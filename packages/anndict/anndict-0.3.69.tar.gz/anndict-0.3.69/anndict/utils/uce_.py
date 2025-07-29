"""
This module contains wrappers for UCE (the universal cell embedding).
Note: this is mainly included for instructional purposes because it will be slow without a gpu.
"""
import subprocess

def uce_adata(
    adata_paths: list[str]
) -> None:
    """
    Runs the eval_single_anndata.py script for each specified :class:`AnnData` path. 
    This function is included largely for instructional purposes and will be 
    restrictivley slow without a gpu.

    Parameters
    ----------
    adata_paths
        A list of paths to the ``.h5ad`` files to be processed.

    Returns
    -------
    None

    Notes
    -----
    Writes the output to the ``./uce_wd/`` directory.

    This function constructs the command to run the ``eval_single_anndata.py`` script 
    with specified arguments and then executes the command using :func:`subprocess.run`.

    The function assumes that a uce-compatible conda environment is already activated 
    and the working directory is correctly set to UCE (i.e. as in https://github.com/snap-stanford/UCE)

    Examples
    --------
    .. code-block:: python

        uce_adata(["../dat/liver.h5ad", "../dat/kidney.h5ad"])
        > # Output is written to the ./uce_wd/ directory
    """
    for adata_path in adata_paths:
        # Command to run the python script with the specified arguments
        command = [
            'accelerate', 'launch', 'eval_single_anndata.py',
            '--adata_path', adata_path,
            '--dir', './uce_wd/',
            '--species', 'human',
            '--model_loc', './model_files/33l_8ep_1024t_1280.torch',
            '--filter', 'True',
            '--batch_size', '25',
            '--nlayers', '33'
        ]

        # Run the command
        subprocess.run(command, check=True)
