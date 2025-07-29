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


def predict_splicing(seqmat_obj, position: int, engine: str = 'spliceai', context: int = 15000, 
                    inplace: bool = False) -> Union[object, pd.DataFrame]:
    """
    Predict splicing probabilities at a given position using the specified engine.

    Args:
        seqmat_obj: SeqMat object with sequence data and indices
        position (int): The genomic position to predict splicing probabilities for.
        engine (str): The prediction engine to use. Supported: 'spliceai', 'pangolin'.
        context (int): Total sequence length for prediction (default: 15000). 
                      For SpliceAI, this results in predictions for central 5000 nucleotides.
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
    
    # For SpliceAI with 15000 total context, extract context/2 on each side of the position
    # Note: clone is inclusive, so we need -1 to get exactly context nucleotides
    half_context = context // 2
    target = seqmat_obj.clone(position - half_context, position + half_context - 1)
    
    # Check if target clone resulted in empty sequence
    if len(target.seq) == 0:
        raise ValueError(f"No sequence data found around position {position} with context {context}")
    
    seq, indices = target.seq, target.index
    
    # Validate indices array is not empty
    if len(indices) == 0:
        raise ValueError(f"No indices found in sequence around position {position}")
    
    # Find relative position within the context window
    rel_pos = np.abs(indices - position).argmin()
    left_missing, right_missing = max(0, half_context - rel_pos), max(0, half_context - (len(seq) - rel_pos))
    
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

    # Ensure we have exactly the expected context length
    if len(seq) != context:
        # Adjust to exact context length
        if len(seq) > context:
            # Trim excess from both sides
            excess = len(seq) - context
            trim_left = excess // 2
            trim_right = excess - trim_left
            seq = seq[trim_left:len(seq)-trim_right] if trim_right > 0 else seq[trim_left:]
            indices = indices[trim_left:len(indices)-trim_right] if trim_right > 0 else indices[trim_left:]
        elif len(seq) < context:
            # Pad to reach exact context length
            deficit = context - len(seq)
            pad_left = deficit // 2
            pad_right = deficit - pad_left
            seq = 'N' * pad_left + seq + 'N' * pad_right
            
            step = -1 if getattr(seqmat_obj, 'rev', False) else 1
            if pad_left > 0:
                left_extend = np.arange(indices[0] - step * pad_left, indices[0], step)
            else:
                left_extend = np.array([], dtype=indices.dtype)
            if pad_right > 0:
                right_extend = np.arange(indices[-1] + step, indices[-1] + step * (pad_right + 1), step)
            else:
                right_extend = np.array([], dtype=indices.dtype)
            
            indices = np.concatenate([left_extend, indices, right_extend])

    # Run the splicing prediction engine
    donor_probs, acceptor_probs = run_splicing_engine(seq=seq, engine=engine)
    
    # For SpliceAI with 15000 input, predictions are already for the central 5000 nucleotides
    # Map predictions back to the correct genomic coordinates
    if engine == 'spliceai':
        pred_len = len(donor_probs)
        # SpliceAI returns predictions for central region, calculate the offset
        if len(seq) == context and pred_len == 5000:
            # With 15000 input, predictions cover central 5000 nucleotides (positions 5000-9999)
            central_start = context // 2 - pred_len // 2  # 7500 - 2500 = 5000
            central_end = central_start + pred_len        # 5000 + 5000 = 10000
            seq = seq[central_start:central_end]
            indices = indices[central_start:central_end]
        # If different configuration, use all available predictions
    
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