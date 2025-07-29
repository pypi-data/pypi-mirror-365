"""
This module contains the core functions of AnnDictionary. This includes:

- The AdataDict class
- functions to iterate over AdataDict objects
- functions to build, write, read, and concatenate AdataDict objects

"""

from .adata_dict_utils import (  # type: ignore
    to_nested_tuple,
    to_nested_list,
    set_var_index_func,
    set_obs_index_func

)

from .adata_dict_fapply import (  # type: ignore
    adata_dict_fapply,
    adata_dict_fapply_return,

)

from .adata_dict import (  # type: ignore
    AdataDict,

)

from .read import (  # type: ignore
    #read and write AdataDict class
    read_adata_dict,

    #read h5ads directly into an AdataDict class
    read_adata_dict_from_h5ad,

)


from .write import (  # type: ignore
    #write AdataDict class
    write_adata_dict,

)


from .build import (  # type: ignore
    #build an AdataDict from an adata in memory
    build_adata_dict,

)


from .add_stratification import (  # type: ignore
    #add another stratification
    add_stratification,

)


from .concatenate import (  # type: ignore

    #concatenate an AdataDict into a single adata
    concatenate_adata_dict,

)


from .utils import (  # type: ignore

    #create single-column combined column for all strata_keys
    check_and_create_stratifier,
)

__all__ = [
    "AdataDict",
    "to_nested_tuple",
    "to_nested_list",
    "adata_dict_fapply",
    "adata_dict_fapply_return",
    "read_adata_dict",
    "write_adata_dict",
    "read_adata_dict_from_h5ad",
    "build_adata_dict",
    "add_stratification",
    "concatenate_adata_dict",
    "check_and_create_stratifier",

]
