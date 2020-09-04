from dataclasses import dataclass

import numpy as np
import torchaudio

from lhotse.features.base import register_extractor, TorchaudioFeatureExtractor
from lhotse.utils import Seconds


@dataclass
class SpectrogramConfig:
    # Note that `snip_edges` parameter is missing from config: in order to simplify the relationship between
    #  the duration and the number of frames, we are always setting `snip_edges` to False.
    dither: float = 0.0
    window_type: str = "povey"
    # Note that frame_length and frame_shift will be converted to milliseconds before torchaudio/Kaldi sees them
    frame_length: Seconds = 0.025
    frame_shift: Seconds = 0.01
    remove_dc_offset: bool = True
    round_to_power_of_two: bool = True
    energy_floor: float = 1e-10
    min_duration: float = 0.0
    preemphasis_coefficient: float = 0.97
    raw_energy: bool = True


@register_extractor
class Spectrogram(TorchaudioFeatureExtractor):
    """Log spectrogram feature extractor based on ``torchaudio.compliance.kaldi.spectrogram`` function."""
    name = 'spectrogram'
    config_type = SpectrogramConfig
    feature_fn = staticmethod(torchaudio.compliance.kaldi.spectrogram)

    @staticmethod
    def mix(features_a: np.ndarray, features_b: np.ndarray, energy_scaling_factor_b: float) -> np.ndarray:
        # Torchaudio returns log-power spectrum, hence the need for logsumexp
        return np.log(np.exp(features_a) + energy_scaling_factor_b * np.exp(features_b))

    @staticmethod
    def compute_energy(features: np.ndarray) -> float:
        # Torchaudio returns log-power spectrum, hence the need for exp before the sum
        return float(np.sum(np.exp(features)))