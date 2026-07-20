"""Text class definitions and synthesis parameters.

This module defines categories for different types of texts and a
PARAMS dictionary containing configuration values used by the synthesis
of noisy speech.
"""

from enum import Enum

class Textclasses(Enum):
    """Enum for categories of test texts used in the pipeline.

    Members:
        NUMBER: Numeric strings
        NAME: names of f.e. persons, places or companies
        NATURAL_TEXT: Longer natural-sounding sentences
    """
    NUMBER = 0
    NAME = 1
    NATURAL_TEXT = 2

PARAMS = {
    Textclasses.NUMBER: {
        "noise_layers": 2,
        "volumes": [0.8, 1.0],
        "speeds": [0.8, 1.0, 1.3],
        "num_interrupts": 1,
        "len_interrupts": 0.1,
        "snr_lower": 20.0,
        "snr_upper": 30.0,
        "total_snrlevels": 2
    },

    Textclasses.NAME: {
        "noise_layers": 1,
        "volumes": [0.9, 1.0],
        "speeds": [0.9, 1.0, 1.2],
        "num_interrupts": 1,
        "len_interrupts": 0.1,
        "snr_lower": 20.0,
        "snr_upper": 40.0,
        "total_snrlevels": 2

    },

    Textclasses.NATURAL_TEXT: {
        "noise_layers": 2,
        "volumes": [1.0],
        "speeds": [1.0],
        "num_interrupts": 3,
        "len_interrupts": 0.2,
        "snr_lower": 10.0,
        "snr_upper": 20.0,
        "total_snrlevels": 2

    }
}
