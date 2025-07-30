#!/usr/bin/env python3
"""
snipit-mc Python API

This module provides a Python interface for snipit-mc (multicolor) functionality,
allowing users to generate SNP visualizations programmatically.

Example usage:
    from snipit import snipit_plot, SnipitConfig
    
    # Basic usage
    snipit_plot("alignment.fasta", output_file="my_plot", colour_palette="nature")
    
    # Advanced usage with configuration
    config = SnipitConfig(
        colour_palette="vangogh",
        width=12,
        height=8,
        format="pdf"
    )
    snipit_plot("alignment.fasta", config=config)
"""

import os
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Optional, List, Union, Dict, Any
from pathlib import Path

# Import existing snipit functionality
from snipit.scripts import snp_functions as sfunks
from snipit import command


@dataclass
class SnipitConfig:
    """Configuration class for snipit plotting parameters.
    
    This class provides a convenient way to configure all snipit parameters
    for programmatic use.
    
    Attributes:
        sequence_type (str): Input sequence type: 'nt' or 'aa'. Default: 'nt'
        reference (str): Reference sequence ID. Default: first sequence
        labels (str): Path to CSV file with sequence labels
        label_headers (str): Column headers for label CSV. Default: 'name,label'
        genbank (str): Path to GenBank file for gene annotations
        
        # Mode options
        recombi_mode (bool): Enable recombination mode. Default: False
        recombi_references (str): Comma-separated sequence IDs for recombination
        cds_mode (bool): Assume sequence is coding sequence. Default: False
        
        # Output options
        output_dir (str): Output directory. Default: current directory
        output_file (str): Output file name stem. Default: 'snp_plot'
        write_snps (bool): Write SNPs to CSV file. Default: False
        format (str): Output format (png, jpg, pdf, svg, tiff). Default: 'png'
        
        # Figure options
        height (float): Figure height. Default: auto
        width (float): Figure width. Default: auto
        size_option (str): Sizing options: 'expand' or 'scale'
        solid_background (bool): Use solid background. Default: False
        colour_palette (str): Color palette name. Default: 'classic'
        flip_vertical (bool): Flip plot orientation. Default: False
        sort_by_mutation_number (bool): Sort by SNP count. Default: False
        sort_by_id (bool): Sort alphabetically by ID. Default: False
        sort_by_mutations (str): Sort by bases at specific positions
        
        # SNP options
        show_indels (bool): Include indels in plot. Default: False
        include_positions (str): Positions to include (e.g., '100-150')
        exclude_positions (str): Positions to exclude (e.g., '223 224')
        ambig_mode (str): Handle ambiguous bases: 'all', 'snps', 'exclude'. Default: 'exclude'
    """
    
    # Input options
    sequence_type: str = 'nt'
    reference: Optional[str] = None
    labels: Optional[str] = None
    label_headers: str = 'name,label'
    genbank: Optional[str] = None
    
    # Mode options
    recombi_mode: bool = False
    recombi_references: Optional[str] = None
    cds_mode: bool = False
    
    # Output options
    output_dir: Optional[str] = None
    output_file: str = 'snp_plot'
    write_snps: bool = False
    format: str = 'png'
    
    # Figure options
    height: float = 0
    width: float = 0
    size_option: Optional[str] = None
    solid_background: bool = False
    colour_palette: str = 'classic'
    flip_vertical: bool = False
    sort_by_mutation_number: bool = False
    sort_by_id: bool = False
    sort_by_mutations: Optional[str] = None
    
    # SNP options
    show_indels: bool = False
    include_positions: Optional[str] = None
    exclude_positions: Optional[str] = None
    ambig_mode: str = 'exclude'
    
    def to_args(self, alignment_file: str) -> List[str]:
        """Convert configuration to command-line arguments format."""
        args = [alignment_file]
        
        # Input options
        args.extend(['-t', self.sequence_type])
        if self.reference:
            args.extend(['-r', self.reference])
        if self.labels:
            args.extend(['-l', self.labels])
        if self.label_headers != 'name,label':
            args.extend(['--l-header', self.label_headers])
        if self.genbank:
            args.extend(['-g', self.genbank])
        
        # Mode options
        if self.recombi_mode:
            args.append('--recombi-mode')
        if self.recombi_references:
            args.extend(['--recombi-references', self.recombi_references])
        if self.cds_mode:
            args.append('--cds-mode')
        
        # Output options
        if self.output_dir:
            args.extend(['-d', self.output_dir])
        args.extend(['-o', self.output_file])
        if self.write_snps:
            args.append('-s')
        args.extend(['-f', self.format])
        
        # Figure options
        if self.height > 0:
            args.extend(['--height', str(self.height)])
        if self.width > 0:
            args.extend(['--width', str(self.width)])
        if self.size_option:
            args.extend(['--size-option', self.size_option])
        if self.solid_background:
            args.append('--solid-background')
        args.extend(['-c', self.colour_palette])
        if self.flip_vertical:
            args.append('--flip-vertical')
        if self.sort_by_mutation_number:
            args.append('--sort-by-mutation-number')
        if self.sort_by_id:
            args.append('--sort-by-id')
        if self.sort_by_mutations:
            args.extend(['--sort-by-mutations', self.sort_by_mutations])
        
        # SNP options
        if self.show_indels:
            args.append('--show-indels')
        if self.include_positions:
            args.extend(['--include-positions', self.include_positions])
        if self.exclude_positions:
            args.extend(['--exclude-positions', self.exclude_positions])
        if self.ambig_mode != 'exclude':
            args.extend(['--ambig-mode', self.ambig_mode])
        
        return args


def snipit_plot(
    alignment_file: Union[str, Path],
    config: Optional[SnipitConfig] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate a SNP visualization plot using snipit-mc.
    
    This is the main function for creating SNP plots programmatically.
    
    Args:
        alignment_file (str or Path): Path to the input alignment FASTA file
        config (SnipitConfig, optional): Configuration object with plot parameters
        **kwargs: Additional parameters that override config settings
        
    Returns:
        dict: Dictionary containing plot information including:
            - output_files: List of generated output files
            - config: Final configuration used
            - success: Boolean indicating success
            
    Raises:
        FileNotFoundError: If alignment file doesn't exist
        ValueError: If invalid parameters are provided
        
    Example:
        >>> from snipit import snipit_plot, SnipitConfig
        >>> 
        >>> # Basic usage
        >>> result = snipit_plot("alignment.fasta", colour_palette="nature")
        >>> print(f"Generated: {result['output_files']}")
        >>>
        >>> # Advanced usage
        >>> config = SnipitConfig(
        ...     colour_palette="vangogh",
        ...     width=12,
        ...     height=8,
        ...     format="pdf",
        ...     genbank="reference.gb"
        ... )
        >>> result = snipit_plot("alignment.fasta", config=config)
    """
    
    # Convert to Path object for easier handling
    alignment_path = Path(alignment_file)
    if not alignment_path.exists():
        raise FileNotFoundError(f"Alignment file not found: {alignment_file}")
    
    # Use provided config or create default
    if config is None:
        config = SnipitConfig()
    
    # Override config with any kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown parameter: {key}")
    
    # Convert config to command-line arguments
    args = config.to_args(str(alignment_path))
    
    try:
        # Run snipit command
        result = command.main(args)
        
        # Determine output files
        output_files = []
        if config.output_dir:
            output_dir = Path(config.output_dir)
        else:
            output_dir = alignment_path.parent
            
        # Main plot file
        plot_file = output_dir / f"{config.output_file}.{config.format}"
        if plot_file.exists():
            output_files.append(str(plot_file))
            
        # SNP CSV file if requested
        if config.write_snps:
            snp_file = output_dir / f"{config.output_file}_snps.csv"
            if snp_file.exists():
                output_files.append(str(snp_file))
        
        return {
            'success': True,
            'output_files': output_files,
            'config': config,
            'message': f"Successfully generated {len(output_files)} file(s)"
        }
        
    except Exception as e:
        return {
            'success': False,
            'output_files': [],
            'config': config,
            'error': str(e),
            'message': f"Failed to generate plot: {str(e)}"
        }


def get_color_palettes() -> Dict[str, Dict[str, str]]:
    """
    Get information about available color palettes.
    
    Returns:
        dict: Dictionary with palette information including descriptions
        
    Example:
        >>> from snipit import get_color_palettes
        >>> palettes = get_color_palettes()
        >>> for name, info in palettes.items():
        ...     print(f"{name}: {info['description']}")
    """
    return {
        'classic': {
            'description': 'Traditional SNP visualization colors',
            'type': 'nucleotide',
            'suitable_for': 'General purpose'
        },
        'nature': {
            'description': 'High-saturation colors suitable for Nature publications',
            'type': 'nucleotide',
            'suitable_for': 'Scientific publications'
        },
        'nature_extended': {
            'description': 'Nature palette with ambiguous base support',
            'type': 'nucleotide_extended',
            'suitable_for': 'Publications with ambiguous bases'
        },
        'nature_aa': {
            'description': 'Nature palette for amino acid sequences',
            'type': 'amino_acid',
            'suitable_for': 'Protein sequence analysis'
        },
        'morandi': {
            'description': 'Muted, grey-toned colors inspired by Giorgio Morandi',
            'type': 'nucleotide',
            'suitable_for': 'Sophisticated, artistic presentations'
        },
        'morandi_extended': {
            'description': 'Morandi palette with ambiguous base support',
            'type': 'nucleotide_extended',
            'suitable_for': 'Artistic presentations with ambiguous bases'
        },
        'morandi_aa': {
            'description': 'Morandi palette for amino acid sequences',
            'type': 'amino_acid',
            'suitable_for': 'Artistic protein analysis'
        },
        'vangogh': {
            'description': 'Vibrant, expressive colors inspired by Vincent van Gogh',
            'type': 'nucleotide',
            'suitable_for': 'Eye-catching, vibrant presentations'
        },
        'vangogh_extended': {
            'description': 'Van Gogh palette with ambiguous base support',
            'type': 'nucleotide_extended',
            'suitable_for': 'Vibrant presentations with ambiguous bases'
        },
        'vangogh_aa': {
            'description': 'Van Gogh palette for amino acid sequences',
            'type': 'amino_acid',
            'suitable_for': 'Vibrant protein analysis'
        },
        'monet': {
            'description': 'Soft impressionist pastels inspired by Claude Monet',
            'type': 'nucleotide',
            'suitable_for': 'Soft, elegant presentations'
        },
        'monet_extended': {
            'description': 'Monet palette with ambiguous base support',
            'type': 'nucleotide_extended',
            'suitable_for': 'Elegant presentations with ambiguous bases'
        },
        'monet_aa': {
            'description': 'Monet palette for amino acid sequences',
            'type': 'amino_acid',
            'suitable_for': 'Elegant protein analysis'
        },
        'matisse': {
            'description': 'Bold, pure colors inspired by Henri Matisse',
            'type': 'nucleotide',
            'suitable_for': 'Bold, modern presentations'
        },
        'matisse_extended': {
            'description': 'Matisse palette with ambiguous base support',
            'type': 'nucleotide_extended',
            'suitable_for': 'Bold presentations with ambiguous bases'
        },
        'matisse_aa': {
            'description': 'Matisse palette for amino acid sequences',
            'type': 'amino_acid',
            'suitable_for': 'Bold protein analysis'
        },
        'primary': {
            'description': 'Primary colors',
            'type': 'nucleotide',
            'suitable_for': 'Simple, clear presentations'
        },
        'purine-pyrimidine': {
            'description': 'Color by base type (purine/pyrimidine)',
            'type': 'nucleotide',
            'suitable_for': 'Chemical classification focus'
        },
        'greyscale': {
            'description': 'Monochrome visualization',
            'type': 'nucleotide',
            'suitable_for': 'Print-friendly, black and white'
        },
        'wes': {
            'description': 'Wes Anderson inspired palette',
            'type': 'nucleotide',
            'suitable_for': 'Vintage, aesthetic presentations'
        },
        'verity': {
            'description': 'Pink/purple theme',
            'type': 'nucleotide',
            'suitable_for': 'Distinctive color scheme'
        },
        'ugene': {
            'description': 'UGENE software colors for amino acids',
            'type': 'amino_acid',
            'suitable_for': 'Protein analysis (UGENE compatibility)'
        }
    }


def validate_alignment(alignment_file: Union[str, Path]) -> Dict[str, Any]:
    """
    Validate an alignment file for snipit compatibility.
    
    Args:
        alignment_file (str or Path): Path to alignment FASTA file
        
    Returns:
        dict: Validation results including:
            - valid: Boolean indicating if file is valid
            - num_sequences: Number of sequences
            - alignment_length: Length of alignment
            - sequence_ids: List of sequence IDs
            - issues: List of any issues found
            
    Example:
        >>> from snipit import validate_alignment
        >>> result = validate_alignment("alignment.fasta")
        >>> if result['valid']:
        ...     print(f"Valid alignment with {result['num_sequences']} sequences")
        ... else:
        ...     print(f"Issues found: {result['issues']}")
    """
    alignment_path = Path(alignment_file)
    result = {
        'valid': False,
        'num_sequences': 0,
        'alignment_length': 0,
        'sequence_ids': [],
        'issues': []
    }
    
    if not alignment_path.exists():
        result['issues'].append(f"File not found: {alignment_file}")
        return result
    
    try:
        from Bio import SeqIO
        
        sequences = []
        sequence_ids = []
        lengths = []
        
        for record in SeqIO.parse(str(alignment_path), "fasta"):
            sequences.append(str(record.seq))
            sequence_ids.append(record.id)
            lengths.append(len(record.seq))
        
        if not sequences:
            result['issues'].append("No sequences found in file")
            return result
        
        result['num_sequences'] = len(sequences)
        result['sequence_ids'] = sequence_ids
        
        # Check alignment length consistency
        if len(set(lengths)) > 1:
            result['issues'].append(f"Inconsistent sequence lengths: {set(lengths)}")
        else:
            result['alignment_length'] = lengths[0]
        
        # Check for duplicate IDs
        if len(sequence_ids) != len(set(sequence_ids)):
            duplicates = [id for id in sequence_ids if sequence_ids.count(id) > 1]
            result['issues'].append(f"Duplicate sequence IDs found: {set(duplicates)}")
        
        # If no issues found so far, mark as valid
        if not result['issues']:
            result['valid'] = True
        
    except Exception as e:
        result['issues'].append(f"Error reading file: {str(e)}")
    
    return result


# Convenience functions for specific use cases
def quick_plot(alignment_file: Union[str, Path], palette: str = "nature", **kwargs) -> Dict[str, Any]:
    """Quick plot with common settings."""
    config = SnipitConfig(colour_palette=palette, **kwargs)
    return snipit_plot(alignment_file, config=config)


def publication_plot(
    alignment_file: Union[str, Path], 
    palette: str = "nature",
    width: float = 12,
    format: str = "pdf",
    **kwargs
) -> Dict[str, Any]:
    """Generate a publication-ready plot."""
    config = SnipitConfig(
        colour_palette=palette,
        width=width,
        format=format,
        solid_background=True,
        **kwargs
    )
    return snipit_plot(alignment_file, config=config)


def protein_plot(alignment_file: Union[str, Path], palette: str = "nature_aa", **kwargs) -> Dict[str, Any]:
    """Generate a plot for protein sequences."""
    config = SnipitConfig(
        sequence_type="aa",
        colour_palette=palette,
        **kwargs
    )
    return snipit_plot(alignment_file, config=config)


def genbank_plot(
    alignment_file: Union[str, Path],
    genbank_file: Union[str, Path],
    palette: str = "nature",
    **kwargs
) -> Dict[str, Any]:
    """Generate a plot with GenBank gene annotations."""
    config = SnipitConfig(
        colour_palette=palette,
        genbank=str(genbank_file),
        **kwargs
    )
    return snipit_plot(alignment_file, config=config)