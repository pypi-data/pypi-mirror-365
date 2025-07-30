"""
JEPA (Joint-Embedding Predictive Architecture) Framework

A powerful self-supervised learning framework for learning representations
by predicting parts of the input from other parts.

Key Features:
- Modular encoder-predictor architecture
- Multi-modal support (vision, NLP, time series, audio)
- High performance with mixed precision and distributed training
- Comprehensive logging and monitoring
- Production-ready CLI interface

Quick Start:
    >>> from jepa import JEPA, JEPATrainer
    >>> from jepa.config import load_config
    >>> 
    >>> # Load configuration and create model
    >>> config = load_config("config/default_config.yaml")
    >>> model = JEPA(config.model)
    >>> trainer = JEPATrainer(model, config)
    >>> trainer.train()

CLI Usage:
    $ python -m jepa.cli train --config config/default_config.yaml
    $ python -m jepa.cli evaluate --config config/default_config.yaml
"""

__version__ = "0.1.0"
__author__ = "Dilip Venkatesh"
__email__ = "your.email@example.com"
__description__ = "Joint-Embedding Predictive Architecture for Self-Supervised Learning"

# Core model components
from .models import JEPA, BaseModel, Encoder, Predictor

# Training framework
from .trainer import JEPATrainer, JEPAEvaluator, create_trainer

# Configuration management
from .config import load_config, save_config, JEPAConfig

# Data utilities
from .data import (
    JEPADataset,
    create_dataset,
    JEPATransforms,
    collate_jepa_batch
)

# Logging system
from .loggers import create_logger, MultiLogger

# Utility functions
from .trainer.utils import (
    count_parameters,
    setup_reproducibility,
    get_device_info,
    EarlyStopping
)

# Package metadata
__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',
    '__description__',
    
    # Core models
    'JEPA',
    'BaseModel', 
    'Encoder',
    'Predictor',
    
    # Training
    'JEPATrainer',
    'JEPAEvaluator',
    'create_trainer',
    
    # Configuration
    'load_config',
    'save_config',
    'JEPAConfig',
    
    # Data
    'JEPADataset',
    'create_dataset',
    'JEPATransforms',
    'collate_jepa_batch',
    
    # Logging
    'create_logger',
    'MultiLogger',
    
    # Utilities
    'count_parameters',
    'setup_reproducibility', 
    'get_device_info',
    'EarlyStopping'
]

# Convenience imports for common use cases
def quick_start(config_path: str):
    """
    Quick start function to begin training with minimal setup.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        JEPATrainer: Configured trainer ready for training
    """
    config = load_config(config_path)
    model = JEPA(config.model)
    trainer = JEPATrainer(model, config)
    return trainer

# Module-level configuration
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())