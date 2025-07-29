"""
Intronator: A Python package for comprehensive splice site analysis and simulation
"""

__version__ = "0.2.0"

"""
Intronator: Comprehensive splice site analysis and simulation package.

Primary APIs:
- comprehensive_splicing_analysis: Complete workflow for splicing mutation analysis
- get_max_missplicing_delta: Get maximum missplicing delta for a mutation
"""

# Primary analysis functions
from .analysis import (
    parse_mutation_id,
    get_max_missplicing_delta,
    comprehensive_splicing_analysis
)

# Straightforward API functions (temporarily commented out)
from .simple_api import (
    MutationalEvent,
    # splicing_analysis,
    # max_splicing_delta,
    # get_missplicing_events,
    # splice_site_changes,
    # full_splicing_report
)

# Core utilities
from .pangolin_utils import pangolin_predict_probs, pang_models
from .spliceai_utils import run_spliceai_seq, sai_models
from .splicing_utils import run_splicing_engine, adjoin_splicing_outcomes, process_epistasis, predict_splicing

# Advanced classes (for custom workflows)
from .transcript_simulation import SpliceSimulator

# Test data
from .test_data import MUT_ID, EPISTASIS_ID

# Monkey-patch SeqMat to add predict_splicing method
try:
    import seqmat
    from .splicing_utils import predict_splicing
    
    def _predict_splicing_method(self, position: int, engine: str = 'spliceai', context: int = 15000, 
                                inplace: bool = False):
        """Monkey-patched predict_splicing method for SeqMat objects."""
        return predict_splicing(self, position, engine, context, inplace)
    
    # Add the method to SeqMat class
    seqmat.SeqMat.predict_splicing = _predict_splicing_method
except ImportError:
    # seqmat not available, skip monkey-patching
    pass

__all__ = [
    # Primary API functions
    "parse_mutation_id",
    "get_max_missplicing_delta",
    "comprehensive_splicing_analysis",
    
    # Straightforward API functions (temporarily commented out)
    "MutationalEvent",
    # "splicing_analysis",
    # "max_splicing_delta",
    # "get_missplicing_events",
    # "splice_site_changes",
    # "full_splicing_report",
    
    # Core utilities
    "pangolin_predict_probs",
    "pang_models", 
    "run_spliceai_seq",
    "sai_models",
    "run_splicing_engine",
    "adjoin_splicing_outcomes", 
    "process_epistasis",
    "predict_splicing",
    
    # Advanced classes
    "SpliceSimulator",
    
    # Test data
    "MUT_ID",
    "EPISTASIS_ID"
]