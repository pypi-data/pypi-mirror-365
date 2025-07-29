# Intronator: Comprehensive Splice Site Analysis Package

## Overview

Intronator is a sophisticated Python package designed for comprehensive analysis of RNA splicing and its perturbations. The package integrates state-of-the-art machine learning models (SpliceAI and Pangolin) with advanced simulation capabilities to predict, analyze, and simulate the effects of genetic variations on RNA splicing patterns.

## Core Intentions and Use Cases

### 1. **Mutation Impact Assessment**
The primary intention is to evaluate how genetic mutations affect RNA splicing:
- **Splice site disruption**: Quantify how mutations weaken canonical splice sites
- **Cryptic splice site activation**: Identify novel splice sites created by mutations
- **Epistatic effects**: Analyze how multiple mutations interact to affect splicing

### 2. **Transcript Isoform Prediction**
Generate and analyze alternative transcript isoforms:
- **Pathway simulation**: Model all possible splicing pathways from a gene
- **Isoform quantification**: Predict relative abundance of different transcript variants
- **Functional consequences**: Assess protein-coding potential of alternative isoforms

### 3. **Clinical Genomics Applications**
Support variant interpretation in medical genetics:
- **Pathogenicity assessment**: Evaluate splicing impact of patient variants
- **Therapeutic target identification**: Find splicing modulators for treatment
- **Precision medicine**: Personalized splicing profiles for treatment decisions

## Package Architecture

### Core Components

#### 1. **Splicing Prediction Engines** (`splicing_utils.py`)
- **Unified interface** to multiple prediction models
- **Engine abstraction**: Easy switching between SpliceAI and Pangolin
- **Batch processing**: Efficient analysis of multiple sequences

```python
import intronator

# Run splicing prediction with different engines
donor_probs, acceptor_probs = intronator.run_splicing_engine(
    seq="ATCGATCG...", 
    engine='spliceai'  # or 'pangolin'
)
```

#### 2. **Splice Site Simulation** (`splice_simulation.py`)
- **Graph-based modeling**: Represents all possible splice connections
- **Probabilistic pathways**: Calculates likelihood of different splicing outcomes
- **Missplicing classification**: Categorizes abnormal splicing events

```python
# Create splice simulator
ss = intronator.SpliceSimulator(
    splicing_df=results_df,
    transcript=transcript_obj,
    max_distance=100000
)

# Generate all viable transcripts
for transcript_variant in ss.get_viable_transcripts():
    print(f"Probability: {transcript_variant.path_weight}")
```

#### 3. **Transcript Library Management** (`transcript_analysis.py`)
- **Multi-variant tracking**: Manages reference and mutated transcripts
- **Comparative analysis**: Side-by-side splicing predictions
- **Epistasis detection**: Identifies non-additive mutation effects

```python
# Create transcript library with mutations
tl = intronator.TranscriptLibrary(reference_transcript, mutations)

# Predict splicing for all variants
tl.predict_splicing(position=12345, engine='spliceai', inplace=True)

# Extract results for specific events
event_data = tl.get_event_columns('event')
```

#### 4. **Data Integration and Analysis** (`splicing_utils.py`)
- **Multi-sample joining**: Combine results from different conditions
- **Epistasis quantification**: Calculate additive vs. observed effects
- **Statistical filtering**: Identify significant splicing changes

```python
# Combine multiple splicing predictions
combined_df = intronator.adjoin_splicing_outcomes(
    splicing_predictions={'wt': wt_df, 'mut1': mut1_df, 'epistasis': epi_df},
    transcript=transcript_obj
)

# Process epistatic interactions
significant_epistasis = intronator.process_epistasis(
    combined_df, 
    threshold=0.25
)
```

## Typical Workflows

### Workflow 1: Single Mutation Analysis

```python
import intronator

# Quick mutation impact assessment
mut_id = mutation_object  # Contains gene, position, ref, alt
ss = intronator.splicing_analysis(mut_id, splicing_engine='spliceai')

# Get maximum splicing disruption
max_delta = intronator.max_splicing_delta(mut_id)
print(f"Maximum splicing impact: {max_delta}")

# Analyze proximity to splice sites
proximity = ss.find_splice_site_proximity(mut_id.position)
print(f"Mutation is in {proximity['region']} {proximity['index']}")
```

### Workflow 2: Comprehensive Isoform Analysis

```python
# Create transcript library
reference_transcript = load_transcript("ENST00000123456")
mutations = [(pos1, 'A', 'G'), (pos2, 'C', 'T')]

tl = intronator.TranscriptLibrary(reference_transcript, mutations)
tl.predict_splicing(mutation_position, engine='spliceai', inplace=True)

# Simulate all possible isoforms
ss = intronator.SpliceSimulator(
    tl.get_event_columns('event'), 
    tl.event, 
    feature='event'
)

# Generate transcript variants with metadata
for transcript, metadata in ss.get_viable_transcripts(metadata=True):
    print(f"Isoform {metadata['isoform_id']}: {metadata['isoform_prevalence']:.3f}")
    print(f"Missplicing events: {metadata['summary']}")
```

### Workflow 3: Epistasis Analysis

```python
# Define mutations
mut1 = (12345, 'A', 'G')
mut2 = (12400, 'C', 'T') 
double_mut = [mut1, mut2]

# Create transcript library with all combinations
tl = intronator.TranscriptLibrary(reference_transcript, double_mut)
tl.predict_splicing(12350, engine='spliceai', inplace=True)

# Combine results and detect epistasis
combined_results = intronator.adjoin_splicing_outcomes({
    'wt': tl.ref.pre_mrna.predicted_splicing,
    'mut1': tl.mut1.pre_mrna.predicted_splicing, 
    'mut2': tl.mut2.pre_mrna.predicted_splicing,
    'epistasis': tl.event.pre_mrna.predicted_splicing
}, tl.ref)

# Quantify epistatic effects
epistasis_results = intronator.process_epistasis(combined_results)
print(f"Found {len(epistasis_results)} sites with significant epistasis")
```

## Advanced Features

### 1. **Missplicing Event Classification**
Automatically categorizes splicing abnormalities:
- **PES**: Partial Exon Skipping
- **ES**: Complete Exon Skipping  
- **PIR**: Partial Intron Retention
- **IR**: Complete Intron Retention
- **NE**: Novel Exon creation

### 2. **Multi-Engine Prediction**
Leverages multiple AI models:
- **SpliceAI**: CNN-based splice site prediction
- **Pangolin**: Transformer-based splicing analysis
- **Ensemble methods**: Combine predictions for improved accuracy

### 3. **GPU Acceleration**
Automatic hardware optimization:
- **CUDA support**: NVIDIA GPU acceleration
- **MPS support**: Apple Silicon GPU acceleration  
- **CPU fallback**: Automatic degradation for compatibility

### 4. **Extensible Architecture**
Designed for future expansion:
- **Plugin system**: Easy addition of new prediction engines
- **Custom models**: Support for user-trained models
- **API compatibility**: Integration with existing genomics pipelines

## Integration with Genomics Ecosystems

### Bioinformatics Pipelines
- **VEP integration**: Variant Effect Predictor compatibility
- **ANNOVAR support**: Annotation pipeline integration
- **Clinical databases**: ClinVar and OMIM compatibility

### Research Applications
- **Population genetics**: Large-scale variant impact studies
- **Disease genetics**: Pathogenic variant characterization
- **Therapeutic development**: Splice-modulating drug discovery

## Performance Considerations

### Computational Requirements
- **Memory**: 4-8GB RAM for typical analyses
- **GPU**: Optional but recommended for large datasets
- **Storage**: Models require ~2GB disk space

### Scalability
- **Batch processing**: Efficient handling of multiple mutations
- **Parallel execution**: Multi-core CPU utilization
- **Cloud deployment**: Container-ready for scalable analysis

## Future Directions

### Planned Enhancements
1. **Additional prediction models**: Integration of newer ML architectures
2. **Tissue-specific models**: Cell-type aware splicing predictions  
3. **Temporal dynamics**: Time-course splicing analysis
4. **3D structure integration**: Spatial context in splicing decisions

### Community Features
- **Model sharing**: User-contributed prediction models
- **Benchmark datasets**: Standardized evaluation metrics
- **Documentation**: Comprehensive tutorials and examples

## Conclusion

Intronator represents a comprehensive solution for splice site analysis, bridging the gap between raw genomic variants and their functional consequences on RNA processing. By integrating state-of-the-art AI models with sophisticated simulation capabilities, it enables researchers and clinicians to understand and predict the complex landscape of alternative splicing in human health and disease.

The package's modular design ensures it can grow with the field, incorporating new models and methods as they become available, while maintaining a consistent and user-friendly interface for the genomics community.