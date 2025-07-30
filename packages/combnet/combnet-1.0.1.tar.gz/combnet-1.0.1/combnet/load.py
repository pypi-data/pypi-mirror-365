import json
from pathlib import Path

import combnet

import torchaudio
import torch


###############################################################################
# Loading utilities
###############################################################################


def partition(dataset):
    """Load partitions for dataset"""
    with open(combnet.PARTITION_DIR / f'{dataset}.json') as file:
        return json.load(file)

def audio(file):
    """Load audio from disk"""
    path = Path(file)
    if path.suffix.lower() == '.mp3':
        try:
            audio, sample_rate = torchaudio.load(path, format='mp3')
        except RuntimeError:
            raise RuntimeError(
                'Failed to load mp3 file, make sure ffmpeg<=4.3 is installed')
    else:
        audio, sample_rate = torchaudio.load(file)

    # Maybe resample
    return combnet.resample(audio, sample_rate)

def model(checkpoint=combnet.DEFAULT_CHECKPOINT) -> torch.nn.Module:
    state_dict = torch.load(checkpoint, map_location='cpu', weights_only=True)
    if 'model' in state_dict:
        state_dict = state_dict['model']

    model = combnet.Model()

    model.load_state_dict(state_dict)

    return model