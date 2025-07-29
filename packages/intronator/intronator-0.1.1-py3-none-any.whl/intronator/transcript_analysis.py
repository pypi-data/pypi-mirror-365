from .splicing_utils import adjoin_splicing_outcomes
from .splice_simulation import SpliceSimulator

__all__ = ['TranscriptLibrary', 'splicing_analysis', 'max_splicing_delta']


class TranscriptLibrary:
    """
    A class for managing multiple transcript variants and their splicing predictions.
    
    Handles reference transcripts and mutations, providing unified interface for
    splicing analysis across different variants.
    """
    
    def __init__(self, reference_transcript, mutations):
        """
        Initialize TranscriptLibrary with reference transcript and mutations.
        
        Args:
            reference_transcript: Reference transcript object
            mutations: List of mutations as (pos, ref, alt) tuples
        """
        self.ref = reference_transcript.clone()
        self.event = reference_transcript.clone()
        self._transcripts = {'ref': self.ref, 'event': self.event}

        # Apply all mutations to 'event'
        for i, (pos, ref, alt) in enumerate(mutations):
            self.event.pre_mrna.apply_mutations((pos, ref, alt))
            if len(mutations) > 1:
                t = reference_transcript.clone()
                t.pre_mrna.apply_mutations((pos, ref, alt))
                self._transcripts[f'mut{i+1}'] = t
                setattr(self, f'mut{i+1}', t)

        # Make 'ref' and 'event' accessible as attributes too
        setattr(self, 'ref', self.ref)
        setattr(self, 'event', self.event)

    def predict_splicing(self, pos, engine='spliceai', inplace=False):
        """
        Predict splicing for all transcript variants.
        
        Args:
            pos: Position for splicing prediction
            engine: Splicing prediction engine ('spliceai' or 'pangolin')
            inplace: Whether to modify object in place
            
        Returns:
            Self if inplace=True, otherwise splicing results DataFrame
        """
        self.splicing_predictions = {
            k: t.pre_mrna.predict_splicing(pos, engine=engine, inplace=True)
            for k, t in self._transcripts.items()
        }
        self.splicing_results = adjoin_splicing_outcomes(
            {k: t.pre_mrna.predicted_splicing for k, t in self._transcripts.items()},
            self.ref
        )
        if inplace:
            return self
        else:
            return self.splicing_results

    def get_event_columns(self, event_name, sites=('donors', 'acceptors')):
        """
        Extract selected columns from splicing_results for a given event name.
        
        Args:
            event_name: Name of the event (e.g., 'event', 'mut1', etc.)
            sites: Tuple of site types ('donors', 'acceptors')
            
        Returns:
            DataFrame with selected columns
            
        Raises:
            ValueError: If predict_splicing() hasn't been run yet
        """
        metrics = (f'{event_name}_prob', 'ref_prob', 'annotated')
        if not hasattr(self, 'splicing_results'):
            raise ValueError("You must run predict_splicing() first.")

        cols = [(site, metric) for site in sites for metric in metrics]
        return self.splicing_results.loc[:, cols]

    def __getitem__(self, key):
        """Get transcript by key."""
        return self._transcripts[key]

    def __iter__(self):
        """Iterate over transcript items."""
        return iter(self._transcripts.items())


def splicing_analysis(mut_id, transcript_id=None, splicing_engine='spliceai'):
    """
    Perform comprehensive splicing analysis for a mutation.
    
    Args:
        mut_id: Mutation identifier or object with gene and position attributes
        transcript_id: Specific transcript ID (optional)
        splicing_engine: Engine for splicing prediction ('spliceai' or 'pangolin')
        
    Returns:
        SpliceSimulator object for further analysis
        
    Note:
        This function expects mut_id to have 'gene' and 'position' attributes,
        and assumes Gene class is available in the environment.
    """
    # Note: This function assumes Gene class is available in the calling environment
    # You may need to import it or pass it as a parameter
    try:
        from .gene_utils import Gene  # Placeholder import - adjust as needed
    except ImportError:
        raise ImportError("Gene class not available. Please ensure gene utilities are imported.")
    
    reference_transcript = (Gene.from_file(mut_id.gene)
                          .transcript(transcript_id)
                          .generate_pre_mrna()
                          .generate_mature_mrna()
                          .generate_protein())
    
    tl = TranscriptLibrary(reference_transcript, [mut_id])
    splicing_results = (tl.predict_splicing(mut_id.position, engine=splicing_engine, inplace=True)
                       .get_event_columns('event'))
    
    ss = SpliceSimulator(splicing_results, tl.event, feature='event', max_distance=100_000_000)
    return ss


def max_splicing_delta(mut_id, transcript_id=None, splicing_engine='spliceai', organism='hg38'):
    """
    Calculate maximum splicing delta for a mutation.
    
    Args:
        mut_id: Mutation identifier or object with gene and position attributes
        transcript_id: Specific transcript ID (optional)
        splicing_engine: Engine for splicing prediction ('spliceai' or 'pangolin')
        organism: Organism reference genome (default: 'hg38')
        
    Returns:
        Maximum splicing delta value
        
    Note:
        This function expects mut_id to have 'gene' and 'position' attributes,
        and assumes Gene class is available in the environment.
    """
    try:
        from .gene_utils import Gene  # Placeholder import - adjust as needed
    except ImportError:
        raise ImportError("Gene class not available. Please ensure gene utilities are imported.")
    
    reference_transcript = (Gene.from_file(mut_id.gene, organism=organism)
                          .transcript(transcript_id)
                          .generate_pre_mrna()
                          .generate_mature_mrna()
                          .generate_protein())
    
    tl = TranscriptLibrary(reference_transcript, [mut_id])
    splicing_results = (tl.predict_splicing(mut_id.position, engine=splicing_engine, inplace=True)
                       .get_event_columns('event'))
    
    ss = SpliceSimulator(splicing_results, tl.event, feature='event', max_distance=100_000_000)
    return ss.max_splicing_delta('event_prob')