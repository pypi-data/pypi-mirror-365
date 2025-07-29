# Load models
#
# __all__ = ['pangolin_predict_probs']
 # Load models
import torch
import numpy as np
import sys

try:
    from pkg_resources import resource_filename
    from pangolin.model import *
    PANGOLIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Pangolin not available - {e}")
    PANGOLIN_AVAILABLE = False

pang_model_nums = [0, 1, 2, 3, 4, 5, 6, 7]
pang_models = []

def get_best_device():
    """Get the best available device for computation."""
    if sys.platform == 'darwin' and torch.backends.mps.is_available():
        try:
            # Test MPS availability
            torch.tensor([1.0], device="mps")
            return torch.device("mps")
        except RuntimeError:
            print("Warning: MPS not available, falling back to CPU")
            return torch.device("cpu")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")

device = get_best_device()
print(f"Pangolin loaded to {device}.")

# Initialize models with improved error handling
if PANGOLIN_AVAILABLE:
    try:
        for i in pang_model_nums:
            for j in range(1, 6):
                try:
                    model = Pangolin(L, W, AR).to(device)
                    
                    # Load weights with proper device mapping
                    model_path = resource_filename("pangolin", f"models/final.{j}.{i}.3")
                    weights = torch.load(model_path, weights_only=True, map_location=device)
                    
                    model.load_state_dict(weights)
                    model.eval()
                    pang_models.append(model)
                    
                except Exception as e:
                    print(f"Warning: Failed to load Pangolin model {j}.{i}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error initializing Pangolin models: {e}")
        pang_models = []
else:
    print("Pangolin models not loaded - install pangolin package")


def pang_one_hot_encode(seq: str) -> np.ndarray:
    """One-hot encode DNA sequence for Pangolin model.
    
    Args:
        seq: DNA sequence string
        
    Returns:
        One-hot encoded array of shape (len(seq), 4)
        
    Raises:
        ValueError: If sequence contains invalid characters
    """
    if not isinstance(seq, str):
        raise TypeError(f"Expected string, got {type(seq).__name__}")
    
    IN_MAP = np.asarray([[0, 0, 0, 0],  # N or unknown
                         [1, 0, 0, 0],  # A
                         [0, 1, 0, 0],  # C
                         [0, 0, 1, 0],  # G
                         [0, 0, 0, 1]]) # T
    
    # Validate sequence
    valid_chars = set('ACGTN')
    if not all(c.upper() in valid_chars for c in seq):
        raise ValueError("Sequence contains invalid characters (only A, C, G, T, N allowed)")
    
    # Convert to numeric representation
    seq = seq.upper().replace('A', '1').replace('C', '2')
    seq = seq.replace('G', '3').replace('T', '4').replace('N', '0')
    
    try:
        seq_array = np.asarray(list(map(int, list(seq))))
        return IN_MAP[seq_array.astype('int8')]
    except (ValueError, IndexError) as e:
        raise ValueError(f"Failed to encode sequence: {e}") from e



def pangolin_predict_probs(true_seq: str, models: list, just_ss: bool = False) -> tuple[list, list]:
    """Predict splice site probabilities using Pangolin models.
    
    Args:
        true_seq: DNA sequence (should be padded with 5000 bases on each side)
        models: List of trained Pangolin models
        just_ss: If True, only use splice site-specific models
        
    Returns:
        Tuple of (donor_probs, acceptor_probs) as lists
        
    Raises:
        ValueError: If sequence is invalid or models are not loaded
        RuntimeError: If model prediction fails
    """
    if not PANGOLIN_AVAILABLE:
        raise RuntimeError("Pangolin package not available - install with: pip install git+https://github.com/tkzeng/Pangolin.git")
        
    if not models:
        raise ValueError("No Pangolin models loaded")
        
    if not isinstance(true_seq, str):
        raise TypeError(f"Expected string, got {type(true_seq).__name__}")
        
    if len(true_seq) < 10000:
        raise ValueError(f"Sequence too short: {len(true_seq)} (expected >= 10000)")
    
    # Select model indices based on mode
    model_nums = [0, 2, 4, 6] if just_ss else [0, 1, 2, 3, 4, 5, 6, 7]
    INDEX_MAP = {0: 1, 1: 2, 2: 4, 3: 5, 4: 7, 5: 8, 6: 10, 7: 11}

    seq = true_seq
    true_seq = true_seq[5000:-5000]
    
    # Vectorized dinucleotide detection
    acceptor_dinucleotide = np.array([true_seq[i - 2:i] == 'AG' for i in range(len(true_seq))])
    donor_dinucleotide = np.array([true_seq[i+1:i+3] == 'GT' for i in range(len(true_seq))])

    try:
        # Encode sequence
        seq_encoded = pang_one_hot_encode(seq).T
        seq_tensor = torch.from_numpy(np.expand_dims(seq_encoded, axis=0)).float().to(device)

        scores = []
        for j, model_num in enumerate(model_nums):
            model_scores = []
            
            # Average across 5 models for each model type
            model_start = 5 * j
            model_end = min(5 * j + 5, len(models))
            
            for model in models[model_start:model_end]:
                try:
                    with torch.no_grad():
                        output = model(seq_tensor)
                        score = output[0][INDEX_MAP[model_num], :].cpu().numpy()
                        model_scores.append(score)
                except Exception as e:
                    print(f"Warning: Model prediction failed: {e}")
                    continue
            
            if model_scores:
                scores.append(np.mean(model_scores, axis=0))
            else:
                print(f"Warning: No valid predictions for model type {model_num}")
                scores.append(np.zeros(len(true_seq)))

        # Combine predictions
        splicing_pred = np.array(scores).max(axis=0)
        donor_probs = [splicing_pred[i] * donor_dinucleotide[i] for i in range(len(true_seq))]
        acceptor_probs = [splicing_pred[i] * acceptor_dinucleotide[i] for i in range(len(true_seq))]
        
        return donor_probs, acceptor_probs
        
    except Exception as e:
        raise RuntimeError(f"Pangolin prediction failed: {e}") from e