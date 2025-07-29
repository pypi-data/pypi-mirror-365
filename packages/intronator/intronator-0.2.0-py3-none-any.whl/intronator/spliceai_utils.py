import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import os
import sys
import tensorflow as tf
import numpy as np
from keras.models import load_model
from importlib import resources


# Force device selection with error handling
def get_best_tensorflow_device():
    """Get the best available TensorFlow device."""
    try:
        # Check for discrete GPU first
        gpu_devices = tf.config.list_physical_devices('GPU')
        if gpu_devices:
            return '/GPU:0'
        
        # Check for MPS on macOS (Apple Silicon)
        if sys.platform == 'darwin':
            try:
                # Try to create a simple operation on MPS device
                with tf.device('/device:GPU:0'):
                    test_tensor = tf.constant([1.0, 2.0, 3.0])
                    result = tf.reduce_sum(test_tensor)
                    return '/device:GPU:0'
            except Exception:
                # Try alternative MPS syntax
                try:
                    with tf.device('GPU:0'):
                        test_tensor = tf.constant([1.0, 2.0, 3.0])
                        result = tf.reduce_sum(test_tensor)
                        return 'GPU:0'
                except Exception:
                    pass
                    
        return '/CPU:0'
    except Exception as e:
        print(f"Warning: Device selection failed, using CPU: {e}")
        return '/CPU:0'

device = get_best_tensorflow_device()

# Model loading paths with error handling
def load_spliceai_models():
    """Load SpliceAI models with proper error handling."""
    try:
        if sys.platform == 'darwin':
            model_filenames = [f"models/spliceai{i}.h5" for i in range(1, 6)]
            model_paths = [resources.files('spliceai').joinpath(f) for f in model_filenames]
        else:
            model_paths = [f"/tamir2/nicolaslynn/tools/SpliceAI/spliceai/models/spliceai{i}.h5"
                           for i in range(1, 6)]
        
        # Load models onto correct device
        models = []
        with tf.device(device):
            for i, model_path in enumerate(model_paths):
                try:
                    model = load_model(str(model_path))
                    models.append(model)
                except Exception as e:
                    print(f"Warning: Failed to load SpliceAI model {i+1}: {e}")
                    continue
        
        if not models:
            raise RuntimeError("No SpliceAI models could be loaded")
            
        return models
        
    except Exception as e:
        print(f"Error loading SpliceAI models: {e}")
        return []

sai_models = load_spliceai_models()

# Display device info
device_info = {
    '/GPU:0': 'GPU',
    '/device:GPU:0': 'MPS (Apple Silicon)',
    'GPU:0': 'MPS (Apple Silicon)', 
    '/CPU:0': 'CPU'
}.get(device, device)

print(f"SpliceAI loaded to {device_info}.")

def one_hot_encode(seq: str) -> np.ndarray:
    """One-hot encode DNA sequence for SpliceAI model.
    
    Args:
        seq: DNA sequence string
        
    Returns:
        One-hot encoded array of shape (len(seq), 4)
        
    Raises:
        ValueError: If sequence contains invalid characters
    """
    if not isinstance(seq, str):
        raise TypeError(f"Expected string, got {type(seq).__name__}")
    
    # Validate sequence
    valid_chars = set('ACGTN')
    if not all(c.upper() in valid_chars for c in seq):
        raise ValueError("Sequence contains invalid characters (only A, C, G, T, N allowed)")
    
    encoding_map = np.asarray([[0, 0, 0, 0],  # N or unknown
                               [1, 0, 0, 0],  # A
                               [0, 1, 0, 0],  # C
                               [0, 0, 1, 0],  # G
                               [0, 0, 0, 1]]) # T

    # Convert to numeric representation
    seq = seq.upper().replace('A', '\x01').replace('C', '\x02')
    seq = seq.replace('G', '\x03').replace('T', '\x04').replace('N', '\x00')

    try:
        return encoding_map[np.frombuffer(seq.encode('latin1'), np.int8) % 5]
    except Exception as e:
        raise ValueError(f"Failed to encode sequence: {e}") from e


def sai_predict_probs(seq: str, models: list) -> tuple[np.ndarray, np.ndarray]:
    """
    Predicts the donor and acceptor junction probability of each
    NT in seq using SpliceAI.

    Args:
        seq: DNA sequence string (should include context padding)
        models: List of trained SpliceAI models
        
    Returns:
        Tuple of (acceptor_probs, donor_probs) as numpy arrays
        
    Raises:
        ValueError: If sequence is invalid or models are not loaded
        RuntimeError: If model prediction fails
    """
    if not models:
        raise ValueError("No SpliceAI models loaded")
        
    if not isinstance(seq, str):
        raise TypeError(f"Expected string, got {type(seq).__name__}")
        
    if len(seq) < 1000:
        raise ValueError(f"Sequence too short: {len(seq)} (expected >= 1000)")
    
    try:
        # Encode sequence
        x = one_hot_encode(seq)[None, :]
        
        # Get predictions from all models
        predictions = []
        for i, model in enumerate(models):
            try:
                pred = model.predict(x, verbose=0)
                predictions.append(pred)
            except Exception as e:
                print(f"Warning: Model {i+1} prediction failed: {e}")
                continue
        
        if not predictions:
            raise RuntimeError("All model predictions failed")
            
        # Average predictions across models
        y = np.mean(predictions, axis=0)
        y = y[0, :, 1:].T  # Extract acceptor and donor probabilities
        
        return y[0, :], y[1, :]
        
    except Exception as e:
        raise RuntimeError(f"SpliceAI prediction failed: {e}") from e


def run_spliceai_seq(seq: str, indices: list, threshold: float = 0) -> tuple[dict, dict]:
    """
    Run SpliceAI on a sequence and return splice site predictions above threshold.
    
    Args:
        seq: DNA sequence string
        indices: List of genomic positions corresponding to sequence positions
        threshold: Minimum probability threshold for splice sites
        
    Returns:
        Tuple of (donor_indices, acceptor_indices) as dictionaries mapping position to probability
        
    Raises:
        ValueError: If inputs are invalid
        RuntimeError: If prediction fails
    """
    if not isinstance(seq, str):
        raise TypeError(f"Expected string sequence, got {type(seq).__name__}")
    
    if not isinstance(indices, (list, np.ndarray)):
        raise TypeError(f"Expected list or array for indices, got {type(indices).__name__}")
        
    if len(indices) != len(seq):
        raise ValueError(f"Indices length ({len(indices)}) must match sequence length ({len(seq)})")
    
    if not isinstance(threshold, (int, float)):
        raise TypeError(f"Threshold must be numeric, got {type(threshold).__name__}")
    
    try:
        # Get splice site predictions
        ref_seq_acceptor_probs, ref_seq_donor_probs = sai_predict_probs(seq, sai_models)
        
        # Filter by threshold
        acceptor_indices = {pos: prob for pos, prob in zip(indices, ref_seq_acceptor_probs) if prob >= threshold}
        donor_indices = {pos: prob for pos, prob in zip(indices, ref_seq_donor_probs) if prob >= threshold}
        
        return donor_indices, acceptor_indices
        
    except Exception as e:
        raise RuntimeError(f"SpliceAI sequence analysis failed: {e}") from e