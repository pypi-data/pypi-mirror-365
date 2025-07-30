import argparse
import shutil
from pathlib import Path

import combnet


###############################################################################
# Entry point
###############################################################################


def main(config, dataset, gpu=None):
    """Train from configuration"""
    # Create output directory
    directory = combnet.RUNS_DIR / combnet.CONFIG
    directory.mkdir(parents=True, exist_ok=True)

    # Save configuration(s)
    for conf in config:
        try:
            shutil.copyfile(conf, directory / conf.name)
        except shutil.SameFileError:
            import warnings
            warnings.warn('Skipping config copy, config in run dir is being used directly!')

    # Train
    combnet.train(dataset, directory, gpu=gpu)


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Train a model')
    parser.add_argument(
        '--config',
        type=Path,
        default=[combnet.DEFAULT_CONFIGURATION],
        help='The configuration file',
        nargs='+')
    parser.add_argument(
        '--dataset',
        default='giantsteps',
        help='The datasets to train on')
    parser.add_argument(
        '--gpu',
        default=None,
        help='The gpu index to use')

    return parser.parse_args()


main(**vars(parse_args()))
