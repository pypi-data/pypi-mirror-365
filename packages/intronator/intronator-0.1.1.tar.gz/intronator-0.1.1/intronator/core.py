"""
Core functionality for intronator package
"""

import seqmat
from .pangolin_utils import pangolin_predict_probs, pang_models
from .spliceai_utils import run_spliceai_seq, sai_models


def hello_intronator():
    """
    Simple hello function to verify package setup
    """
    return "Hello from intronator!"


def check_seqmat_compatibility():
    """
    Check if seqmat is properly imported and accessible
    """
    try:
        return f"seqmat is available: {seqmat.__version__}"
    except AttributeError:
        return "seqmat is available but version not found"
    except Exception as e:
        return f"seqmat import failed: {e}"


def get_model_status():
    """
    Check the status of loaded splice prediction models
    """
    status = {
        "pangolin_models": len(pang_models),
        "spliceai_models": len(sai_models)
    }
    return status