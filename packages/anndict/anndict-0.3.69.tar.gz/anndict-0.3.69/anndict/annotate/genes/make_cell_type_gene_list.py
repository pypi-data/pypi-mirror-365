#make_cell_type_gene_list.py
"""
Use LLMs create gene lists for a given cell type (with species awareness). 
This automates manual curation of these lists. 
"""
import ast

from anndict.utils import enforce_semantic_list
from anndict.llm import call_llm, retry_call_llm, extract_list_from_ai_string


def ai_make_cell_type_gene_list(
    cell_type: str,
    species: str,
    list_length: str = None
    ) -> list[str]:
    """
    Returns a list of specific marker genes for the input ``cell_type``.

    Parameters
    ------------
    cell_type
        The cell type to get marker genes for.

    species
        The species to consider.

    list_length
        Qualitative length of the marker gene list. Can be anything like 
        ``'short'`` or ``'long'``. Try ``'long'`` if you are having trouble 
        getting valid genes that are present in your dataset.

    Returns
    --------
    A list of marker genes.
    """
    # Enforce that cell_type is a semantic string
    enforce_semantic_list([cell_type])

    # Initialize the conversation with the system prompt
    messages = [
        {"role": "system", "content": "You are a terse molecular biologist."}
    ]

    # Step 1: Ask about canonical marker genes
    step1_prompt = (
        f"Discuss canonical {cell_type} marker genes in {species}. "
        f"Then, narrow your discussion to highly specific marker genes of this cell type."
    )
    messages.append({"role": "user", "content": step1_prompt})

    # Get the response from the assistant
    response1 = call_llm(
        messages=messages,
        max_tokens=500,
        temperature=0
    )
    messages.append({"role": "assistant", "content": response1})

    # Step 2: If extensive_list is True, ask for a longer list
    if list_length:
        step2_prompt = f"Provide a {list_length} list of genes."
        messages.append({"role": "user", "content": step2_prompt})

        # Get the response from the assistant
        response2 = call_llm(
            messages=messages,
            max_tokens=750,
            temperature=0
        )
        messages.append({"role": "assistant", "content": response2})

    # Step 3: Ask for the genes as a Python list
    step3_prompt = "Provide these as a python list as they would be present in scRNA-seq data."
    messages.append({"role": "user", "content": step3_prompt})

    def process_response(response):
        gene_list = extract_list_from_ai_string(response)
        return ast.literal_eval(gene_list)

    def failure_handler(cell_type):
        print(f"Failed to generate list for: {cell_type}")
        return []

    call_llm_kwargs = {
        'max_tokens': 1000,
        'temperature': 0
    }

    failure_handler_kwargs = {'cell_type': cell_type}

    gene_list = retry_call_llm(
        messages=messages,
        process_response=process_response,
        failure_handler=failure_handler,
        call_llm_kwargs=call_llm_kwargs,
        failure_handler_kwargs=failure_handler_kwargs
    )

    return gene_list
