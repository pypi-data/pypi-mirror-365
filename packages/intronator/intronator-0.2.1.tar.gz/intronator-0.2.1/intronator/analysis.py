"""
Primary analysis interface for intronator package.

Provides the comprehensive splicing analysis workflow and essential utilities.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional, Union
from .splicing_utils import run_splicing_engine, process_epistasis
import seqmat


def parse_mutation_id(mut_id: str) -> Tuple[str, int, str, str]:
    """Parse mutation ID string into components.
    
    Args:
        mut_id: Mutation string like 'GENE:CHR:POS:REF:ALT' or 'POS:REF:ALT'
        
    Returns:
        Tuple of (gene, position, ref_allele, alt_allele)
    """
    parts = mut_id.split(':')
    if len(parts) >= 5:
        return parts[0], int(parts[2]), parts[3], parts[4]
    elif len(parts) >= 3:
        return None, int(parts[0]), parts[1], parts[2]
    else:
        raise ValueError(f"Invalid mutation string format: {mut_id}")


def get_max_missplicing_delta(mut_id: str, 
                            transcript=None,
                            engine: str = 'spliceai',
                            gene_name: Optional[str] = None) -> float:
    """
    Get the maximum missplicing event delta for a mutation ID using simplified workflow.
    
    Args:
        mut_id: Mutation ID string (e.g., 'GENE:CHR:POS:REF:ALT')
        transcript: Reference transcript object (if None, uses seqmat.Gene.from_file)
        engine: Splicing engine to use for prediction
        gene_name: Gene name to load if transcript is None
        
    Returns:
        Maximum absolute delta value for the mutation's splicing impact
    """
    # Parse mutation from ID
    gene, position, ref_allele, alt_allele = parse_mutation_id(mut_id)
    
    # Get transcript if not provided
    if transcript is None:
        if gene_name is None:
            if gene:
                gene_name = gene
            else:
                raise ValueError("Must provide either transcript or gene_name")
        
        transcript = seqmat.Gene.from_file(gene_name).transcript()
    
    # Simplified workflow for max delta calculation
    # 1) Generate pre-mRNA and get reference sequence
    transcript.generate_pre_mrna()
    ref_seq = transcript.pre_mrna.seq
    
    # 2) Apply mutation and get variant sequence  
    transcript.pre_mrna.apply_mutations((position, ref_allele, alt_allele))
    var_seq = transcript.pre_mrna.seq
    
    # 3) Run splicing engine on both sequences
    refp = run_splicing_engine(ref_seq, engine=engine)
    varp = run_splicing_engine(var_seq, engine=engine)
    
    # 4) Calculate deltas and return maximum
    donor_deltas = np.array(varp[0]) - np.array(refp[0])
    acceptor_deltas = np.array(varp[1]) - np.array(refp[1])
    
    max_donor_delta = np.abs(donor_deltas).max()
    max_acceptor_delta = np.abs(acceptor_deltas).max()
    
    return max(max_donor_delta, max_acceptor_delta)


def comprehensive_splicing_analysis(mut_id: str, 
                                   transcript=None,
                                   engine: str = 'spliceai',
                                   gene_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Comprehensive splicing analysis using simplified workflow:
    1. Parse mutation ID and get transcript from seqmat
    2. Generate pre-mRNA and get reference sequence
    3. Apply mutation and get variant sequence
    4. Run splicing engine on both sequences
    5. Calculate deltas and generate results
    
    Args:
        mut_id: Mutation ID string (e.g., 'GENE:CHR:POS:REF:ALT')
        transcript: Reference transcript object (if None, uses seqmat.Gene.from_file)
        engine: Splicing engine to use for prediction
        gene_name: Gene name to load if transcript is None
        
    Returns:
        Dictionary containing:
            - max_delta: Maximum absolute delta value
            - summary: Analysis summary
            - donor_deltas: Array of donor probability differences
            - acceptor_deltas: Array of acceptor probability differences
    """
    # Parse mutation from ID
    gene, position, ref_allele, alt_allele = parse_mutation_id(mut_id)
    
    # Get transcript if not provided
    if transcript is None:
        if gene_name is None:
            if gene:
                gene_name = gene
            else:
                raise ValueError("Must provide either transcript or gene_name")
        
        transcript = seqmat.Gene.from_file(gene_name).transcript()
    
    # Simplified workflow:
    # 1) Generate pre-mRNA and get reference sequence
    transcript.generate_pre_mrna()
    ref_seq = transcript.pre_mrna.seq
    
    # 2) Apply mutation and get variant sequence  
    transcript.pre_mrna.apply_mutations((position, ref_allele, alt_allele))
    var_seq = transcript.pre_mrna.seq
    
    # 3) Run splicing engine on both sequences
    refp = run_splicing_engine(ref_seq, engine=engine)
    varp = run_splicing_engine(var_seq, engine=engine)
    
    # 4) Calculate deltas
    donor_deltas = np.array(varp[0]) - np.array(refp[0])
    acceptor_deltas = np.array(varp[1]) - np.array(refp[1])
    
    max_donor_delta = np.abs(donor_deltas).max()
    max_acceptor_delta = np.abs(acceptor_deltas).max()
    max_delta = max(max_donor_delta, max_acceptor_delta)
    
    # Create summary
    summary = {
        'mutation': f"{position}:{ref_allele}>{alt_allele}",
        'gene': gene,
        'engine': engine,
        'max_delta': max_delta,
        'sequence_length': len(ref_seq),
        'total_predictions': len(donor_deltas)
    }
    
    return {
        'max_delta': max_delta,
        'summary': summary,
        'donor_deltas': donor_deltas,
        'acceptor_deltas': acceptor_deltas
    }


__all__ = [
    'parse_mutation_id',
    'get_max_missplicing_delta',
    'comprehensive_splicing_analysis'
]