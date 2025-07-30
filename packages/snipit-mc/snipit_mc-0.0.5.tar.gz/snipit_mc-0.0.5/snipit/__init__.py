_program = "snipit"
__version__ = "0.0.5"

# Import API functions for easy access
try:
    from .api import (
        snipit_plot,
        SnipitConfig,
        get_color_palettes,
        validate_alignment,
        quick_plot,
        publication_plot,
        protein_plot,
        genbank_plot
    )
    
    __all__ = [
        'snipit_plot',
        'SnipitConfig', 
        'get_color_palettes',
        'validate_alignment',
        'quick_plot',
        'publication_plot',
        'protein_plot',
        'genbank_plot'
    ]
except ImportError:
    # During build, dependencies might not be available
    __all__ = []
