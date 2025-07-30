"""
Straightforward API functions for common splicing analysis workflows.

Provides simple, direct functions that handle the complete analysis pipeline
from mutation ID to results.
"""

import pandas as pd
from typing import Optional, Union, List, Tuple
from .transcript_simulation import SpliceSimulator


class MutationalEvent:
    """
    Simple mutation event handler that can parse mutation IDs and manage multiple mutations.
    """
    
    def __init__(self, mut_id: Union[str, List[str]]):
        """
        Initialize from mutation ID string or list of mutation IDs.
        
        Args:
            mut_id: Single mutation ID ('GENE:CHR:POS:REF:ALT') or list of IDs
        """
        if isinstance(mut_id, str):
            if '|' in mut_id:
                # Handle epistasis format 'MUT1|MUT2|MUT3'
                mut_ids = mut_id.split('|')
            else:
                mut_ids = [mut_id]
        else:
            mut_ids = mut_id
        
        self.mutations = []
        for mid in mut_ids:
            parts = mid.split(':')
            if len(parts) >= 5:
                self.mutations.append({
                    'gene': parts[0],
                    'chr': parts[1],
                    'position': int(parts[2]),
                    'ref': parts[3],
                    'alt': parts[4]
                })
            else:
                raise ValueError(f"Invalid mutation ID format: {mid}")
        
        # Set primary attributes from first mutation
        if self.mutations:
            self.gene = self.mutations[0]['gene']
            self.position = self.mutations[0]['position']
            self.positions = [m['position'] for m in self.mutations]
    
    def compatible(self) -> bool:
        """Check if all mutations are compatible (same gene)."""
        if not self.mutations:
            return False
        genes = set(m['gene'] for m in self.mutations)
        return len(genes) == 1
    
    def as_tuples(self) -> List[Tuple[int, str, str]]:
        """Convert to list of (position, ref, alt) tuples for TranscriptLibrary."""
        return [(m['position'], m['ref'], m['alt']) for m in self.mutations]
    
    def __iter__(self):
        """Allow iteration over mutations for TranscriptLibrary compatibility."""
        return iter(self.as_tuples())
    
    def __len__(self):
        """Return number of mutations."""
        return len(self.mutations)
    
    def __getitem__(self, index):
        """Get mutation by index as tuple."""
        return self.as_tuples()[index]
    
    def __str__(self):
        """String representation of the mutational event."""
        if len(self.mutations) == 1:
            m = self.mutations[0]
            return f"{m['gene']}:{m['chr']}:{m['position']}:{m['ref']}:{m['alt']}"
        else:
            return '|'.join([f"{m['gene']}:{m['chr']}:{m['position']}:{m['ref']}:{m['alt']}" 
                            for m in self.mutations])


# # NOTE: Functions below are temporarily commented out after removing TranscriptLibrary
# # They can be reimplemented using the simplified workflow if needed
# 
# # def splicing_analysis(mut_id: Union[str, MutationalEvent], 
# #                      transcript_id: Optional[str] = None,
# #                      splicing_engine: str = 'spliceai',
# #                      gene_loader=None) -> SpliceSimulator:
#     """
#     Perform comprehensive splicing analysis for a mutation.
#     
#     Args:
#         mut_id: Mutation ID string or MutationalEvent object
#         transcript_id: Specific transcript ID (optional)
#         splicing_engine: Engine for splicing prediction ('spliceai' or 'pangolin')
#         gene_loader: Function to load genes (e.g., Gene.from_file)
#         
#     Returns:
#         SpliceSimulator object configured for the mutation
#         
#     Example:
#         >>> ss = splicing_analysis('KRAS:12:25227343:G:T')
#         >>> print(ss.max_splicing_delta('event_prob'))
#         >>> variants = list(ss.generate_transcript_variants(max_variants=10))
#     """
#     # Handle mutation ID
#     if isinstance(mut_id, str):
#         m = MutationalEvent(mut_id)
#     else:
#         m = mut_id
#     
#     assert m.compatible(), 'Mutations in event are incompatible'
#     
#     # Load reference transcript
#     if gene_loader is None:
#         raise ValueError("gene_loader function must be provided (e.g., Gene.from_file)")
#     
#     reference_transcript = (gene_loader(m.gene)
#                           .transcript(transcript_id)
#                           .generate_pre_mrna()
#                           .generate_mature_mrna()
#                           .generate_protein())
#     
#     # Create transcript library and predict splicing
#     tl = TranscriptLibrary(reference_transcript, m)
#     tl.predict_splicing(m.position, engine=splicing_engine, inplace=True)
#     
#     # Get the appropriate variant name
#     if len(m) == 1:
#         variant_name = 'mutant'
#     elif len(m) > 1:
#         variant_name = 'combined'
#     else:
#         variant_name = 'event'
#     
#     splicing_results = tl.get_variant_columns(variant_name)
#     
#     # Create and return splice simulator
#     # Get the actual transcript variant
#     if hasattr(tl, variant_name):
#         transcript_variant = getattr(tl, variant_name)
#     else:
#         transcript_variant = tl[variant_name]
#     
#     ss = SpliceSimulator(splicing_results, transcript_variant, feature=variant_name, max_distance=100_000_000)
#     return ss
# 
# 
# def max_splicing_delta(mut_id: Union[str, MutationalEvent],
#                       transcript_id: Optional[str] = None,
#                       splicing_engine: str = 'spliceai',
#                       organism: str = 'hg38',
#                       gene_loader=None) -> float:
#     """
#     Calculate maximum splicing delta for a mutation.
#     
#     Args:
#         mut_id: Mutation ID string or MutationalEvent object
#         transcript_id: Specific transcript ID (optional)
#         splicing_engine: Engine for splicing prediction ('spliceai' or 'pangolin')
#         organism: Reference genome (default: 'hg38')
#         gene_loader: Function to load genes with organism parameter
#         
#     Returns:
#         Maximum splicing delta value (float)
#         
#     Example:
#         >>> delta = max_splicing_delta('KRAS:12:25227343:G:T')
#         >>> print(f"Max delta: {delta}")
#     """
#     # Handle mutation ID
#     if isinstance(mut_id, str):
#         m = MutationalEvent(mut_id)
#     else:
#         m = mut_id
#     
#     assert m.compatible(), 'Mutations in event are incompatible'
#     
#     # Load reference transcript
#     if gene_loader is None:
#         raise ValueError("gene_loader function must be provided (e.g., Gene.from_file)")
#     
#     reference_transcript = (gene_loader(m.gene, organism=organism)
#                           .transcript(transcript_id)
#                           .generate_pre_mrna()
#                           .generate_mature_mrna()
#                           .generate_protein())
#     
#     # Create transcript library and predict splicing
#     tl = TranscriptLibrary(reference_transcript, m)
#     tl.predict_splicing(m.position, engine=splicing_engine, inplace=True)
#     
#     # Get the appropriate variant name
#     if len(m) == 1:
#         variant_name = 'mutant'
#     elif len(m) > 1:
#         variant_name = 'combined'
#     else:
#         variant_name = 'event'
#     
#     splicing_results = tl.get_variant_columns(variant_name)
#     
#     # Create simulator and calculate max delta
#     # Get the actual transcript variant
#     if hasattr(tl, variant_name):
#         transcript_variant = getattr(tl, variant_name)
#     else:
#         transcript_variant = tl[variant_name]
#     
#     ss = SpliceSimulator(splicing_results, transcript_variant, feature=variant_name, max_distance=100_000_000)
#     return ss.calculate_max_splicing_delta(f'{variant_name}_prob')
# 
# 
# def get_missplicing_events(mut_id: Union[str, MutationalEvent],
#                           transcript_id: Optional[str] = None,
#                           splicing_engine: str = 'spliceai',
#                           max_isoforms: int = 100,
#                           gene_loader=None) -> pd.DataFrame:
#     """
#     Get DataFrame of all missplicing events for a mutation.
#     
#     Args:
#         mut_id: Mutation ID string or MutationalEvent object
#         transcript_id: Specific transcript ID (optional)
#         splicing_engine: Engine for splicing prediction
#         max_isoforms: Maximum number of isoforms to analyze
#         gene_loader: Function to load genes
#         
#     Returns:
#         DataFrame with columns: isoform_id, prevalence, event_type, 
#         pes, es, ir, ne, pir, max_delta
#         
#     Example:
#         >>> events_df = get_missplicing_events('KRAS:12:25227343:G:T')
#         >>> print(events_df[['prevalence', 'event_type']].head())
#     """
#     # Get splice simulator
#     ss = splicing_analysis(mut_id, transcript_id, splicing_engine, gene_loader)
#     
#     # Get max delta for reference
#     max_delta = ss.calculate_max_splicing_delta()
#     
#     # Generate variants and collect missplicing events
#     events_data = []
#     for variant, metadata in ss.generate_transcript_variants(
#         include_metadata=True, max_variants=max_isoforms):
#         
#         events_data.append({
#             'isoform_id': getattr(variant, 'path_hash', f'isoform_{len(events_data)}'),
#             'prevalence': getattr(variant, 'path_probability', 1.0 / (len(events_data) + 1)),
#             'event_type': metadata.get('summary', 'Normal'),
#             'pes': metadata.get('pes', ''),
#             'es': metadata.get('es', ''),
#             'ir': metadata.get('ir', ''),
#             'ne': metadata.get('ne', ''),
#             'pir': metadata.get('pir', ''),
#             'max_delta': max_delta
#         })
#     
#     # Create DataFrame and sort by prevalence
#     events_df = pd.DataFrame(events_data)
#     events_df = events_df.sort_values('prevalence', ascending=False).reset_index(drop=True)
#     events_df['rank'] = range(1, len(events_df) + 1)
#     
#     return events_df
# 
# 
# def splice_site_changes(mut_id: Union[str, MutationalEvent],
#                        transcript_id: Optional[str] = None,
#                        splicing_engine: str = 'spliceai',
#                        threshold: float = 0.1,
#                        gene_loader=None) -> pd.DataFrame:
#     """
#     Get DataFrame of splice site probability changes above threshold.
#     
#     Args:
#         mut_id: Mutation ID string or MutationalEvent object
#         transcript_id: Specific transcript ID (optional)
#         splicing_engine: Engine for splicing prediction
#         threshold: Minimum absolute change to include (default: 0.1)
#         gene_loader: Function to load genes
#         
#     Returns:
#         DataFrame with splice sites that changed by more than threshold
#         
#     Example:
#         >>> changes = splice_site_changes('KRAS:12:25227343:G:T', threshold=0.2)
#         >>> print(changes[['position', 'site_type', 'ref_prob', 'mut_prob', 'delta']])
#     """
#     # Get splice simulator
#     ss = splicing_analysis(mut_id, transcript_id, splicing_engine, gene_loader)
#     
#     # Collect significant changes
#     changes_data = []
#     
#     # Check donor sites
#     donor_df = ss.donor_df
#     for pos in donor_df.index:
#         ref_prob = donor_df.loc[pos, 'ref_prob']
#         event_prob = donor_df.loc[pos, 'event_prob']
#         delta = event_prob - ref_prob
#         
#         if abs(delta) >= threshold:
#             changes_data.append({
#                 'position': pos,
#                 'site_type': 'donor',
#                 'ref_prob': ref_prob,
#                 'mut_prob': event_prob,
#                 'delta': delta,
#                 'annotated': donor_df.loc[pos, 'annotated']
#             })
#     
#     # Check acceptor sites
#     acceptor_df = ss.acceptor_df
#     for pos in acceptor_df.index:
#         ref_prob = acceptor_df.loc[pos, 'ref_prob']
#         event_prob = acceptor_df.loc[pos, 'event_prob']
#         delta = event_prob - ref_prob
#         
#         if abs(delta) >= threshold:
#             changes_data.append({
#                 'position': pos,
#                 'site_type': 'acceptor',
#                 'ref_prob': ref_prob,
#                 'mut_prob': event_prob,
#                 'delta': delta,
#                 'annotated': acceptor_df.loc[pos, 'annotated']
#             })
#     
#     # Create DataFrame sorted by absolute delta
#     changes_df = pd.DataFrame(changes_data)
#     if not changes_df.empty:
#         changes_df['abs_delta'] = changes_df['delta'].abs()
#         changes_df = changes_df.sort_values('abs_delta', ascending=False).reset_index(drop=True)
#         changes_df = changes_df.drop('abs_delta', axis=1)
#     
#     return changes_df
# 
# 
# # Convenience wrapper that combines multiple analyses
# def full_splicing_report(mut_id: Union[str, MutationalEvent],
#                         transcript_id: Optional[str] = None,
#                         splicing_engine: str = 'spliceai',
#                         gene_loader=None) -> dict:
#     """
#     Generate comprehensive splicing report for a mutation.
#     
#     Returns dictionary with:
#         - max_delta: Maximum splicing delta
#         - splice_changes: DataFrame of significant splice site changes
#         - missplicing_events: DataFrame of all possible missplicing events
#         - summary: Summary statistics
#     """
#     # Get splice simulator once
#     ss = splicing_analysis(mut_id, transcript_id, splicing_engine, gene_loader)
#     
#     # Calculate max delta
#     max_delta = ss.calculate_max_splicing_delta()
#     
#     # Get splice site changes
#     changes_df = splice_site_changes(mut_id, transcript_id, splicing_engine, 0.1, gene_loader)
#     
#     # Get missplicing events
#     events_df = get_missplicing_events(mut_id, transcript_id, splicing_engine, 50, gene_loader)
#     
#     # Create summary
#     summary = {
#         'mutation': str(mut_id) if isinstance(mut_id, str) else str(mut_id),
#         'max_delta': max_delta,
#         'sites_affected': len(changes_df),
#         'total_isoforms': len(events_df),
#         'dominant_event': events_df.iloc[0]['event_type'] if not events_df.empty else 'Normal',
#         'events_summary': events_df['event_type'].value_counts().to_dict() if not events_df.empty else {}
#     }
#     
#     return {
#         'max_delta': max_delta,
#         'splice_changes': changes_df,
#         'missplicing_events': events_df,
#         'summary': summary
#     }
# 
# 
__all__ = [
    'MutationalEvent',
    # 'splicing_analysis',
    # 'max_splicing_delta',
    # 'get_missplicing_events',
    # 'splice_site_changes',
    # 'full_splicing_report'
]