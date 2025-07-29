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
        var_df = splicing_df.rename(columns={
            'donor_prob': ('donors', f'{label}_prob'),
            'acceptor_prob': ('acceptors', f'{label}_prob'),
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