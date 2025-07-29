"""
Intronator: A Python package for intron analysis
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import hello_intronator, check_seqmat_compatibility, get_model_status
from .pangolin_utils import pangolin_predict_probs, pang_models
from .spliceai_utils import run_spliceai_seq, sai_models
from .splicing_utils import run_splicing_engine, adjoin_splicing_outcomes, process_epistasis
from .splice_simulation import SpliceSimulator
from .transcript_analysis import TranscriptLibrary, splicing_analysis, max_splicing_delta

__all__ = [
    "hello_intronator",
    "check_seqmat_compatibility", 
    "get_model_status",
    "pangolin_predict_probs",
    "pang_models",
    "run_spliceai_seq", 
    "sai_models",
    "run_splicing_engine",
    "adjoin_splicing_outcomes",
    "process_epistasis",
    "SpliceSimulator",
    "TranscriptLibrary",
    "splicing_analysis",
    "max_splicing_delta"
]