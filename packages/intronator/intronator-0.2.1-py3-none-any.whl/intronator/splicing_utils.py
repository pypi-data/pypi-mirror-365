import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union

def run_splicing_engine(seq: Optional[str] = None, engine: str = 'spliceai') -> Tuple[List[float], List[float]]:
    """
    Run the specified splicing engine to predict splice site probabilities on a sequence.

    Args:
        seq: Nucleotide sequence. If None, generates a random sequence.
        engine: Engine name ('spliceai', 'spliceai-pytorch', or 'pangolin').

    Returns:
        Tuple (donor_probs, acceptor_probs) as lists of probability values.

    Raises:
        ValueError: If the engine is not implemented or sequence is invalid.
        ImportError: If required engine modules are not available.
    """

    if seq is None:
        try:
            from seqmat.utils import generate_random_sequence
            seq = generate_random_sequence(15_001)
        except ImportError:
            # Fallback random sequence generation
            import random
            bases = ['A', 'C', 'G', 'T']
            seq = ''.join(random.choices(bases, k=15_001))
    
    # Validate sequence
    if not isinstance(seq, str):
        raise TypeError(f"Sequence must be string, got {type(seq).__name__}")
    if not seq:
        raise ValueError("Sequence cannot be empty")
    
    # Validate nucleotide sequence
    valid_chars = set('ACGTN')
    if not all(c.upper() in valid_chars for c in seq):
        raise ValueError("Sequence contains invalid nucleotides (only A, C, G, T, N allowed)")

    try:
        match engine:
            case 'spliceai':
                from .spliceai_utils import sai_predict_probs, sai_models
                acceptor_probs, donor_probs = sai_predict_probs(seq, models=sai_models)

            case 'pangolin':
                from .pangolin_utils import pangolin_predict_probs, pang_models
                donor_probs, acceptor_probs = pangolin_predict_probs(seq, models=pang_models)

            case _:
                raise ValueError(f"Engine '{engine}' not implemented. Available: 'spliceai', 'pangolin'")
    except ImportError as e:
        raise ImportError(f"Failed to import engine '{engine}': {e}") from e

    return donor_probs, acceptor_probs


def adjoin_splicing_outcomes(splicing_predictions: Dict[str, pd.DataFrame], transcript=None) -> pd.DataFrame:
    """
    Combine splicing predictions for multiple mutations into a multi-index DataFrame.

    Args:
        splicing_predictions: Dictionary where keys are mutation labels (e.g. 'mut1', 'mut2', 'epistasis') and
                            values are DataFrames with splicing predictions.
        transcript: Transcript object with annotated splice sites (optional).

    Returns:
        pd.DataFrame: Multi-index column DataFrame with mutation-specific predictions.
        
    Raises:
        ValueError: If splicing_predictions is empty or contains invalid data.
    """
    if not splicing_predictions:
        raise ValueError("splicing_predictions cannot be empty")
    
    # Validate input DataFrames
    for label, df in splicing_predictions.items():
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected DataFrame for '{label}', got {type(df).__name__}")
        required_cols = ['donor_prob', 'acceptor_prob', 'nucleotides']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"DataFrame for '{label}' missing required columns: {missing_cols}")
    
    dfs = []
    for label, splicing_df in splicing_predictions.items():
        # Use 'ref_prob' for reference variant, keep original name for others
        prob_suffix = 'ref_prob' if label == 'reference' else f'{label}_prob'
        var_df = splicing_df.rename(columns={
            'donor_prob': ('donors', prob_suffix),
            'acceptor_prob': ('acceptors', prob_suffix),
            'nucleotides': ('nts', f'{label}')
        })
        dfs.append(var_df)

    # Concatenate all DataFrames and unify columns
    try:
        full_df = pd.concat(dfs, axis=1)
    except Exception as e:
        raise ValueError(f"Failed to concatenate DataFrames: {e}") from e

    # Ensure MultiIndex columns
    if not isinstance(full_df.columns, pd.MultiIndex):
        full_df.columns = pd.MultiIndex.from_tuples(full_df.columns)

    if transcript is not None:
        full_df[('acceptors', 'annotated')] = full_df.apply(
            lambda row: row.name in transcript.acceptors,
            axis=1
        )

        full_df[('donors', 'annotated')] = full_df.apply(
            lambda row: row.name in transcript.donors,
            axis=1
        )

        full_df.sort_index(axis=1, level=0, inplace=True)
        full_df.sort_index(ascending=not transcript.rev, inplace=True)
    else:
        full_df.sort_index(axis=1, level=0, inplace=True)

    return full_df


def process_epistasis(df: pd.DataFrame, threshold: float = 0.25) -> pd.DataFrame:
    """
    Computes the expected epistasis effect (additive) and residual epistasis
    for both donor and acceptor probabilities.

    Adds new columns under donors and acceptors:
        - expected_epistasis
        - residual_epistasis

    Args:
        df: MultiIndex column DataFrame with keys:
            'wt_prob', 'mut1_prob', 'mut2_prob', 'epistasis_prob'
        threshold: Minimum absolute residual epistasis to include in output

    Returns:
        pd.DataFrame: Filtered DataFrame with expected and residual epistasis columns added.
        
    Raises:
        ValueError: If required columns are missing or threshold is invalid.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(df).__name__}")
    
    if not isinstance(threshold, (int, float)):
        raise TypeError(f"threshold must be numeric, got {type(threshold).__name__}")
    
    if threshold < 0:
        raise ValueError(f"threshold must be non-negative, got {threshold}")
    
    # Validate required columns exist
    required_cols = ['wt_prob', 'mut1_prob', 'mut2_prob', 'epistasis_prob']
    for feature in ['donors', 'acceptors']:
        for col in required_cols:
            if (feature, col) not in df.columns:
                raise ValueError(f"Missing required column: ({feature}, {col})")
    
    for feature in ['donors', 'acceptors']:
        wt = df[feature]['wt_prob']
        mut1 = df[feature]['mut1_prob']
        mut2 = df[feature]['mut2_prob']
        true_epi = df[feature]['epistasis_prob']

        expected = mut1 + mut2 - wt
        residual = true_epi - expected

        df[(feature, 'expected_epistasis')] = expected
        df[(feature, 'residual_epistasis')] = residual

    df = df.sort_index(axis=1, level=0)
    
    # Create mask for significant epistasis
    try:
        mask = (
            df['donors']['residual_epistasis'].abs() > threshold
        ) | (
            df['acceptors']['residual_epistasis'].abs() > threshold
        )
    except KeyError as e:
        raise ValueError(f"Missing required column for epistasis calculation: {e}") from e
    
    filtered_df = df[mask]
    
    # Return empty DataFrame with same structure if no significant epistasis
    if filtered_df.empty:
        return df.iloc[:0].copy()
    
    return filtered_df


def predict_splicing(seqmat_obj, position: int, engine: str = 'spliceai', context: int = 7500, 
                    inplace: bool = False) -> Union[object, pd.DataFrame]:
    """
    Predict splicing probabilities at a given position using the specified engine.

    Args:
        seqmat_obj: SeqMat object with sequence data and indices
        position (int): The genomic position to predict splicing probabilities for.
        engine (str): The prediction engine to use. Supported: 'spliceai', 'pangolin'.
        context (int): The length of the target central region (default: 7500).
        inplace (bool): If True, stores result in seqmat_obj.predicted_splicing and returns seqmat_obj.
                       If False, returns DataFrame directly.

    Returns:
        pd.DataFrame or SeqMat object: A DataFrame containing:
            - position: The genomic position
            - donor_prob: Probability of being a donor splice site
            - acceptor_prob: Probability of being an acceptor splice site
            - nucleotides: The nucleotide sequence at that position

    Raises:
        ValueError: If an unsupported engine is provided.
        IndexError: If the position is not found in the sequence.
    """
    # Validate position is within sequence bounds
    min_index = seqmat_obj.index.min()
    max_index = seqmat_obj.index.max()
    if position < min_index or position > max_index:
        raise ValueError(f"Position {position} is outside sequence bounds [{min_index}, {max_index}]")
    
    # Retrieve extended context (includes flanks) around the position.
    target = seqmat_obj.clone(position - context, position + context)
    
    # Check if target clone resulted in empty sequence
    if len(target.seq) == 0:
        raise ValueError(f"No sequence data found around position {position} with context {context}")
    
    seq, indices = target.seq, target.index
    
    # Validate indices array is not empty
    if len(indices) == 0:
        raise ValueError(f"No indices found in sequence around position {position}")
    
    # Find relative position within the context window
    rel_pos = np.abs(indices - position).argmin()
    left_missing, right_missing = max(0, context - rel_pos), max(0, context - (len(seq) - rel_pos))
    
    if left_missing > 0 or right_missing > 0:
        step = -1 if getattr(seqmat_obj, 'rev', False) else 1

        if left_missing > 0:
            left_pad = np.arange(indices[0] - step * left_missing, indices[0], step)
        else:
            left_pad = np.array([], dtype=indices.dtype)

        if right_missing > 0:
            right_pad = np.arange(indices[-1] + step, indices[-1] + step * (right_missing + 1), step)
        else:
            right_pad = np.array([], dtype=indices.dtype)

        seq = 'N' * left_missing + seq + 'N' * right_missing
        indices = np.concatenate([left_pad, indices, right_pad])

    # Run the splicing prediction engine (function assumed to be defined externally)
    donor_probs, acceptor_probs = run_splicing_engine(seq=seq, engine=engine)
    
    # Trim off the fixed flanks before returning results.
    seq = seq[5000:-5000]
    indices = indices[5000:-5000]
    
    df = pd.DataFrame({
        'position': indices,
        'donor_prob': donor_probs,
        'acceptor_prob': acceptor_probs,
        'nucleotides': list(seq)
    }).set_index('position').round(3)

    df.attrs['name'] = getattr(seqmat_obj, 'name', 'unknown')
    
    if inplace:
        seqmat_obj.predicted_splicing = df
        return seqmat_obj
    else:
        return df


def predict_splicing_from_mutation(mutation_id: str, engine: str = 'spliceai', 
                                  context: int = 7500, transcript_id=None) -> pd.DataFrame:
    """
    Predict splicing probabilities for reference and mutated sequences, calculating deltas.

    Args:
        mutation_id (str): Mutation identifier (format: 'gene:chrom:pos:start:end')
        engine (str): The prediction engine to use. Supported: 'spliceai', 'pangolin'.
        context (int): The length of the target central region (default: 7500).

    Returns:
        pd.DataFrame: A DataFrame containing:
            - position: The genomic position
            - ref_nucleotide: Reference nucleotide
            - mut_nucleotide: Mutated nucleotide
            - ref_donor_prob: Reference donor probability
            - ref_acceptor_prob: Reference acceptor probability
            - mut_donor_prob: Mutated donor probability
            - mut_acceptor_prob: Mutated acceptor probability
            - delta_donor: Change in donor probability
            - delta_acceptor: Change in acceptor probability

    Raises:
        ValueError: If mutation_id format is invalid or mutation position is out of bounds.
    """
    # Parse mutation ID (e.g., 'gene:chrom:pos:start:end')
    parts = mutation_id.split(':')
    if len(parts) != 5:
        raise ValueError("Invalid mutation format - expected 5 parts separated by ':'")
    
    gene, chrom, pos_str, start_str, end_str = parts
    position = int(pos_str)
    start_pos = int(start_str)
    end_pos = int(end_str)
    
        
    # Load gene sequence using seqmat library
    from seqmat import Gene
    ref_seq = Gene.from_file(gene).transcript(transcript_id=transcript_id).generate_pre_mrna()

    var_seq = ref_seq.clone()
    var_seq.pre_mrna.apply_mutations([(position, ref_nucleotide, mut_nucleotide)])
    
    ref_nts, var_nts = ref_seq.seq, var_seq.seq
    ref_indices, var_indices = ref_seq.index, var_seq.index

    # Find relative position within the context window
    rel_pos = np.abs(indices - position).argmin()
    left_missing, right_missing = max(0, context - rel_pos), max(0, context - (len(seq) - rel_pos))
    
    if left_missing > 0 or right_missing > 0:
        step = -1 if getattr(seqmat_obj, 'rev', False) else 1

        if left_missing > 0:
            left_pad = np.arange(indices[0] - step * left_missing, indices[0], step)
        else:
            left_pad = np.array([], dtype=indices.dtype)

        if right_missing > 0:
            right_pad = np.arange(indices[-1] + step, indices[-1] + step * (right_missing + 1), step)
        else:
            right_pad = np.array([], dtype=indices.dtype)

        seq = 'N' * left_missing + seq + 'N' * right_missing
        indices = np.concatenate([left_pad, indices, right_pad])

    # Run splicing prediction on both sequences
    ref_donor_probs, ref_acceptor_probs = run_splicing_engine(seq=ref_seq, engine=engine)
    mut_donor_probs, mut_acceptor_probs = run_splicing_engine(seq=mut_seq, engine=engine)
    
    # Trim off the fixed flanks before returning results
    ref_seq_final = ref_seq[5000:-5000]
    mut_seq_final = mut_seq[5000:-5000]
    indices_final = indices[5000:-5000]
    
    # Calculate deltas
    delta_donor = np.array(mut_donor_probs) - np.array(ref_donor_probs)
    delta_acceptor = np.array(mut_acceptor_probs) - np.array(ref_acceptor_probs)
    
    df = pd.DataFrame({
        'position': indices_final,
        'ref_nucleotide': list(ref_seq_final),
        'mut_nucleotide': list(mut_seq_final),
        'ref_donor_prob': ref_donor_probs,
        'ref_acceptor_prob': ref_acceptor_probs,
        'mut_donor_prob': mut_donor_probs,
        'mut_acceptor_prob': mut_acceptor_probs,
        'delta_donor': delta_donor,
        'delta_acceptor': delta_acceptor
    }).set_index('position').round(3)

    df.attrs['name'] = getattr(seqmat_obj, 'name', 'unknown')
    df.attrs['mutation_id'] = mutation_id
    df.attrs['gene'] = gene
    df.attrs['chromosome'] = chrom
    df.attrs['mutation_position'] = position
    df.attrs['start_position'] = start_pos
    df.attrs['end_position'] = end_pos
    df.attrs['ref_nucleotide'] = ref_nucleotide
    df.attrs['mut_nucleotide'] = mut_nucleotide
    
    return df