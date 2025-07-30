"""
Comprehensive transcript splicing simulation and analysis module.

This module provides unified functionality for:
- Splice site simulation and modeling
- Transcript library management
- Missplicing event analysis
- Graph-based splice site connectivity
"""

import numpy as np
import pandas as pd
from collections import defaultdict
from typing import List, Tuple, Dict, Generator, Any, Optional, Union
from pandas import Series
from dataclasses import dataclass
from enum import Enum


class MissplicingEventType(Enum):
    """Enumeration of missplicing event types."""
    PES = "Partial Exon Skipping"
    ES = "Exon Skipping" 
    PIR = "Partial Intron Retention"
    IR = "Intron Retention"
    NE = "Novel Exon"


@dataclass
class SpliceMetrics:
    """Container for splice site probability metrics."""
    ref_prob: float
    event_prob: float
    annotated: bool = False
    
    @property
    def discovered_delta(self, min_increase: float = 0.2) -> float:
        """Delta for discovered splice sites."""
        if self.annotated:
            return 0.0
        delta = self.event_prob - self.ref_prob
        return delta if delta >= min_increase else 0.0
    
    @property
    def deleted_delta(self) -> float:
        """Delta for deleted/weakened splice sites."""
        if not self.annotated or self.ref_prob <= 0:
            return 0.0
        delta = (self.event_prob - self.ref_prob) / self.ref_prob
        return min(delta, 0.0)  # Only negative deltas
    
    @property
    def priority_score(self) -> float:
        """Combined priority score for splice site."""
        return float(self.annotated) + self.discovered_delta + self.deleted_delta


def compute_hash(items: Union[List, Tuple]) -> int:
    """Compute a stable hash for splice site combinations."""
    return hash(tuple(sorted(items))) % 1000000


class SpliceSimulator:
    """
    Advanced splice site simulation using graph-based modeling.
    
    Models splice site connectivity as a directed graph where nodes represent
    splice sites and edges represent possible splicing connections with
    associated probabilities.
    """

    def __init__(self, 
                 splicing_df: pd.DataFrame, 
                 transcript, 
                 max_distance: int = 100_000_000,
                 feature: str = 'event',
                 min_increase_ratio: float = 0.2):
        """
        Initialize SpliceSimulator.

        Args:
            splicing_df: DataFrame with 'donors' and 'acceptors' columns containing
                       splice site positions and probabilities
            transcript: Transcript object with splice site annotations
            max_distance: Maximum distance for splice site connections
            feature: Feature prefix for probability columns
            min_increase_ratio: Minimum increase threshold for discovered sites
        """
        self.full_df = splicing_df
        self.feature = feature
        self.min_increase_ratio = min_increase_ratio
        self.transcript = transcript
        self.max_distance = max_distance
        
        # Extract transcript properties
        self.rev = transcript.rev
        self.transcript_start = transcript.transcript_start
        self.transcript_end = transcript.transcript_end
        self.donors = transcript.donors
        self.acceptors = transcript.acceptors

        # Build splice site DataFrames
        self._donor_df = None
        self._acceptor_df = None
        self._graph = None

    def _build_splice_df(self, site_type: str) -> pd.DataFrame:
        """
        Build and annotate splice site DataFrame with metrics.

        Args:
            site_type: 'donor' or 'acceptor'

        Returns:
            Annotated DataFrame with priority scores and deltas
        """
        feature_col = f'{self.feature}_prob'
        df = getattr(self.full_df, site_type + 's').copy()
        known_sites = getattr(self, site_type + 's')

        # Ensure all known sites are included
        missing_sites = set(known_sites) - set(df.index)
        if missing_sites:
            missing_df = pd.DataFrame(
                index=list(missing_sites),
                data={
                    'annotated': True,
                    'ref_prob': 1.0,
                    feature_col: 1.0
                }
            )
            df = pd.concat([df, missing_df], axis=0)

        # Ensure required columns exist
        df['annotated'] = df.get('annotated', False).fillna(False).astype(bool)
        df['ref_prob'] = df.get('ref_prob', 0.0).fillna(0.0)
        df[feature_col] = df.get(feature_col, 0.0).fillna(0.0)

        # Sort by genomic position (respect strand orientation)
        df.sort_index(ascending=not self.rev, inplace=True)

        # Calculate deltas and priority scores
        df['discovered_delta'] = np.where(
            ~df['annotated'],
            np.maximum(df[feature_col] - df['ref_prob'], 0),
            0
        )
        df['discovered_delta'] = np.where(
            df['discovered_delta'] >= self.min_increase_ratio, 
            df['discovered_delta'], 
            0
        )

        with np.errstate(divide='ignore', invalid='ignore'):
            df['deleted_delta'] = np.where(
                (df['ref_prob'] > 0) & df['annotated'],
                np.minimum((df[feature_col] - df['ref_prob']) / df['ref_prob'], 0),
                0
            )

        df['priority_score'] = (
            df['annotated'].astype(float) + 
            df['discovered_delta'] + 
            df['deleted_delta']
        )
        
        return df

    @property
    def donor_df(self) -> pd.DataFrame:
        """Get donor splice sites DataFrame."""
        if self._donor_df is None:
            self._donor_df = self._build_splice_df('donor')
        return self._donor_df

    @property
    def acceptor_df(self) -> pd.DataFrame:
        """Get acceptor splice sites DataFrame."""
        if self._acceptor_df is None:
            self._acceptor_df = self._build_splice_df('acceptor')
        return self._acceptor_df

    def _build_node_list(self, site_type: str) -> List[Tuple[int, float]]:
        """Build sorted list of splice site nodes."""
        df = self.donor_df if site_type == 'donor' else self.acceptor_df
        active_sites = df[df['priority_score'] > 0]['priority_score']
        
        # Convert to explicit types to avoid numpy/pandas sorting conflicts
        node_list = [(int(pos), float(score)) for pos, score in active_sites.round(3).items()]
        
        if site_type == 'donor':
            node_list.append((int(self.transcript_end), 1.0))
        else:
            node_list.insert(0, (int(self.transcript_start), 1.0))
        
        # Sort using a simple lambda function
        return sorted(node_list, key=lambda item: item[0], reverse=self.rev)

    @property
    def donor_nodes(self) -> List[Tuple[int, float]]:
        """Get sorted donor nodes."""
        return self._build_node_list('donor')

    @property
    def acceptor_nodes(self) -> List[Tuple[int, float]]:
        """Get sorted acceptor nodes."""
        return self._build_node_list('acceptor')

    def _is_valid_connection(self, pos1: int, pos2: int, 
                           forward_direction: bool = True) -> bool:
        """Check if connection between positions is valid."""
        distance_valid = abs(pos2 - pos1) <= self.max_distance
        
        if forward_direction:
            orientation_valid = (pos2 > pos1) != self.rev
        else:
            orientation_valid = (pos1 > pos2) != self.rev
            
        return distance_valid and orientation_valid

    def _count_intervening_sites(self, start: int, end: int, 
                               site_nodes: List[Tuple[int, float]]) -> int:
        """Count splice sites between start and end positions."""
        if self.rev:
            start, end = end, start
        return sum(1 for pos, _ in site_nodes if start < pos < end)

    def build_splice_graph(self) -> Dict[Tuple[int, str], List[Tuple[int, str, float]]]:
        """
        Build directed graph of splice site connections.
        
        Returns:
            Adjacency list where keys are (position, type) and values are
            lists of (next_position, next_type, probability) tuples
        """
        if self._graph is not None:
            return self._graph
            
        graph = defaultdict(list)
        donor_nodes = self.donor_nodes
        acceptor_nodes = self.acceptor_nodes

        # Connect donors to acceptors
        for d_pos, d_prob in donor_nodes:
            remaining_prob = 1.0
            for a_pos, a_prob in acceptor_nodes:
                if not self._is_valid_connection(d_pos, a_pos):
                    continue
                    
                # Check for intervening sites
                intervening_donors = self._count_intervening_sites(d_pos, a_pos, donor_nodes)
                intervening_acceptors = self._count_intervening_sites(d_pos, a_pos, acceptor_nodes)
                
                if intervening_donors == 0 or intervening_acceptors == 0:
                    connection_prob = min(a_prob, remaining_prob)
                    if connection_prob > 0:
                        graph[(d_pos, 'donor')].append((a_pos, 'acceptor', connection_prob))
                        remaining_prob -= connection_prob
                        
                if remaining_prob <= 0:
                    break

        # Connect acceptors to donors
        for a_pos, a_prob in acceptor_nodes:
            remaining_prob = 1.0
            for d_pos, d_prob in donor_nodes:
                if not self._is_valid_connection(a_pos, d_pos):
                    continue
                    
                intervening_acceptors = self._count_intervening_sites(a_pos, d_pos, acceptor_nodes)
                
                if intervening_acceptors == 0:
                    node_type = 'transcript_end' if d_pos == self.transcript_end else 'donor'
                    connection_prob = min(d_prob, remaining_prob)
                    if connection_prob > 0:
                        graph[(a_pos, 'acceptor')].append((d_pos, node_type, connection_prob))
                        remaining_prob -= connection_prob
                        
                if remaining_prob <= 0:
                    break

        # Connect transcript start to donors
        remaining_prob = 1.0
        for d_pos, d_prob in donor_nodes:
            if not self._is_valid_connection(self.transcript_start, d_pos):
                continue
                
            connection_prob = min(d_prob, remaining_prob)
            if connection_prob > 0:
                graph[(self.transcript_start, 'transcript_start')].append(
                    (d_pos, 'donor', connection_prob)
                )
                remaining_prob -= connection_prob
                
            if remaining_prob <= 0:
                break

        # Normalize probabilities
        for node, connections in graph.items():
            total_prob = sum(prob for _, _, prob in connections)
            if total_prob > 0:
                graph[node] = [
                    (pos, typ, round(prob / total_prob, 4))
                    for pos, typ, prob in connections
                ]

        self._graph = dict(graph)
        return self._graph

    def find_all_paths(self,
                      start: Tuple[int, str],
                      end: Tuple[int, str],
                      max_paths: int = 1000) -> List[Tuple[List[Tuple[int, str]], float]]:
        """
        Find all possible splice paths from start to end.
        
        Args:
            start: Starting node (position, type)
            end: Ending node (position, type) 
            max_paths: Maximum number of paths to return
            
        Returns:
            List of (path, probability) tuples sorted by probability
        """
        graph = self.build_splice_graph()
        paths = []
        
        def dfs(current_node: Tuple[int, str], 
                current_path: List[Tuple[int, str]], 
                current_prob: float):
            if len(paths) >= max_paths:
                return
                
            if current_node == end:
                paths.append((current_path + [current_node], current_prob))
                return
                
            if current_node not in graph:
                return
                
            for next_pos, next_type, edge_prob in graph[current_node]:
                next_node = (next_pos, next_type)
                if next_node not in current_path:  # Avoid cycles
                    dfs(next_node, current_path + [current_node], current_prob * edge_prob)
        
        dfs(start, [], 1.0)
        return sorted(paths, key=lambda x: x[1], reverse=True)

    def generate_transcript_variants(self, 
                                   include_metadata: bool = False,
                                   max_variants: int = 100) -> Generator:
        """
        Generate transcript variants based on splice paths.
        
        Args:
            include_metadata: Whether to include splicing analysis metadata
            max_variants: Maximum number of variants to generate
            
        Yields:
            Transcript objects (with metadata if requested)
        """
        start_node = (self.transcript_start, 'transcript_start')
        end_node = (self.transcript_end, 'transcript_end')
        
        paths = self.find_all_paths(start_node, end_node, max_variants)
        
        for path, probability in paths:
            # Extract splice sites from path
            donors = [pos for pos, typ in path if typ == 'donor']
            acceptors = [pos for pos, typ in path if typ == 'acceptor']
            
            # Create transcript variant
            variant = self.transcript.clone()
            variant.donors = [d for d in donors if d != self.transcript_end]
            variant.acceptors = [a for a in acceptors if a != self.transcript_start]
            variant.path_probability = probability
            variant.path_hash = compute_hash(donors + acceptors)
            
            # Generate mature transcript products
            try:
                variant.generate_mature_mrna().generate_protein()
            except Exception:
                continue  # Skip variants that can't be processed
            
            if include_metadata:
                metadata = self._analyze_splicing_changes(variant)
                metadata['isoform_prevalence'] = probability
                metadata['isoform_id'] = variant.path_hash
                yield variant, metadata
            else:
                yield variant

    def _analyze_splicing_changes(self, variant) -> pd.Series:
        """Analyze splicing changes between reference and variant."""
        events = self._classify_missplicing_events(variant)
        return pd.Series({
            'pes': events.get('PES', ''),
            'pir': events.get('PIR', ''),
            'es': events.get('ES', ''),
            'ne': events.get('NE', ''),
            'ir': events.get('IR', ''),
            'summary': self._summarize_events(events)
        })

    def _classify_missplicing_events(self, variant) -> Dict[str, List[str]]:
        """Classify missplicing events by comparing reference to variant."""
        ref = self.transcript
        ref_introns = getattr(ref, 'introns', [])
        ref_exons = getattr(ref, 'exons', [])
        var_introns = getattr(variant, 'introns', [])
        var_exons = getattr(variant, 'exons', [])
        
        events = defaultdict(list)
        
        # Partial Exon Skipping (PES)
        for i, (r_start, r_end) in enumerate(ref_exons):
            for v_start, v_end in var_exons:
                if self._is_partial_overlap(r_start, r_end, v_start, v_end):
                    events['PES'].append(
                        f'Exon {i+1}/{len(ref_exons)} truncated: '
                        f'({r_start},{r_end}) → ({v_start},{v_end})'
                    )
        
        # Exon Skipping (ES)
        for i, (r_start, r_end) in enumerate(ref_exons):
            if not any(self._sites_match(r_start, r_end, v_start, v_end) 
                      for v_start, v_end in var_exons):
                events['ES'].append(f'Exon {i+1}/{len(ref_exons)} skipped: ({r_start},{r_end})')
        
        # Novel Exons (NE)
        for v_start, v_end in var_exons:
            if not any(self._sites_match(v_start, v_end, r_start, r_end) 
                      for r_start, r_end in ref_exons):
                events['NE'].append(f'Novel exon: ({v_start},{v_end})')
        
        # Intron Retention (IR) and Partial Intron Retention (PIR)
        for i, (r_start, r_end) in enumerate(ref_introns):
            retained = any(self._sites_match(r_start, r_end, v_start, v_end) 
                          for v_start, v_end in var_exons)
            partial = any(self._is_partial_overlap(r_start, r_end, v_start, v_end) 
                         for v_start, v_end in var_exons)
            
            if retained:
                events['IR'].append(f'Intron {i+1}/{len(ref_introns)} retained: ({r_start},{r_end})')
            elif partial:
                events['PIR'].append(f'Intron {i+1}/{len(ref_introns)} partially retained')
        
        return {k: ','.join(v) for k, v in events.items()}

    def _is_partial_overlap(self, r_start: int, r_end: int, 
                           v_start: int, v_end: int) -> bool:
        """Check if regions have partial overlap."""
        if self.rev:
            return ((v_start == r_start and v_end > r_end) or 
                   (v_start < r_start and v_end == r_end))
        else:
            return ((v_start == r_start and v_end < r_end) or 
                   (v_start > r_start and v_end == r_end))

    def _sites_match(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        """Check if splice sites match."""
        return start1 == start2 and end1 == end2

    def _summarize_events(self, events: Dict[str, str]) -> str:
        """Create summary string of missplicing events."""
        active_events = [event_type for event_type, description in events.items() 
                        if description]
        return ','.join(active_events) if active_events else 'Normal'

    def calculate_max_splicing_delta(self, event_column: str = None) -> float:
        """
        Calculate maximum splicing delta across all sites.
        
        Args:
            event_column: Column name for event probabilities
            
        Returns:
            Maximum absolute difference between event and reference probabilities
        """
        if event_column is None:
            event_column = f'{self.feature}_prob'
            
        all_deltas = []
        
        for site_type in ['donors', 'acceptors']:
            df = getattr(self.full_df, site_type)
            if event_column in df.columns and 'ref_prob' in df.columns:
                deltas = (df[event_column] - df['ref_prob']).tolist()
                all_deltas.extend(deltas)
        
        return max(all_deltas, key=abs) if all_deltas else 0.0

    def find_splice_site_proximity(self, position: int) -> pd.Series:
        """
        Find which exon/intron a position falls into and calculate distances.
        
        Args:
            position: Genomic position to analyze
            
        Returns:
            Series with region type, index, and distance information
        """
        def create_result(region: str, index: int, start: int, end: int) -> pd.Series:
            return pd.Series({
                'region': region,
                'index': index + 1,
                "5'_distance": abs(position - min(start, end)),
                "3'_distance": abs(position - max(start, end))
            })

        # Check exons
        if hasattr(self.transcript, 'exons'):
            for i, (start, end) in enumerate(self.transcript.exons):
                if min(start, end) <= position <= max(start, end):
                    return create_result('exon', i, start, end)

        # Check introns
        if hasattr(self.transcript, 'introns'):
            for i, (start, end) in enumerate(self.transcript.introns):
                if min(start, end) <= position <= max(start, end):
                    return create_result('intron', i, start, end)

        # Position not found in transcript
        return pd.Series({
            'region': 'intergenic',
            'index': None,
            "5'_distance": np.inf,
            "3'_distance": np.inf
        })

    def generate_report(self, position: int) -> Dict[str, Any]:
        """
        Generate comprehensive splicing analysis report.
        
        Args:
            position: Position for analysis
            
        Returns:
            Dictionary with analysis results
        """
        proximity = self.find_splice_site_proximity(position)
        
        # Identify significant events
        donor_events = self.donor_df[
            (self.donor_df['deleted_delta'].abs() > 0.2) | 
            (self.donor_df['discovered_delta'] > 0.2)
        ].reset_index()
        
        acceptor_events = self.acceptor_df[
            (self.acceptor_df['deleted_delta'].abs() > 0.2) | 
            (self.acceptor_df['discovered_delta'] > 0.2)
        ].reset_index()
        
        return {
            'position_analysis': proximity.to_dict(),
            'donor_events': donor_events.to_dict('records'),
            'acceptor_events': acceptor_events.to_dict('records'),
            'max_splicing_delta': self.calculate_max_splicing_delta(),
            'total_variants': len(list(self.generate_transcript_variants(max_variants=10)))
        }



__all__ = [
    'SpliceSimulator',
    'MissplicingEventType',
    'SpliceMetrics',
    'compute_hash'
]