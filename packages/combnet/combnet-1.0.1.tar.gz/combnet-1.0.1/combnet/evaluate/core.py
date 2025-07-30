import json

import torch
import torchutil

import combnet


###############################################################################
# Evaluate
###############################################################################


@torchutil.notify('evaluate')
def datasets(
    datasets=combnet.EVALUATION_DATASETS,
    checkpoint=combnet.DEFAULT_CHECKPOINT,
    gpu=None):
    """Perform evaluation"""
    with torch.inference_mode():
        device = torch.device('cpu' if gpu is None else f'cuda:{gpu}')

        # load model with checkpoint
        model = combnet.load.model(checkpoint).to(device)
        model.eval()

        # Containers for results
        overall, granular = {}, {}

        # Per-file metrics
        file_metrics = combnet.evaluate.Metrics()

        # Per-dataset metrics
        dataset_metrics = combnet.evaluate.Metrics()

        # Aggregate metrics over all datasets
        aggregate_metrics = combnet.evaluate.Metrics()

        # Evaluate each dataset
        for dataset in datasets:

            # Reset dataset metrics
            dataset_metrics.reset()

            # loader = combnet.data.loader(dataset, 'test', features=combnet.FEATURES + ['stem'])
            loader = combnet.data.loader(dataset, 'test', features=combnet.FEATURES + ['stem'])

            # Iterate over test set
            for batch in torchutil.iterator(
                loader,
                f'Evaluating {combnet.CONFIG} on {dataset}'
            ):

                # Reset file metrics
                file_metrics.reset()

                (x, y, stem) = batch

                x = x.to(device)
                y = y.to(device)

                z = model(x)

                # Update metrics
                args = (
                    z,
                    y
                )
                file_metrics.update(*args)
                dataset_metrics.update(*args)
                aggregate_metrics.update(*args)

                # Save results
                granular[f'{dataset}/{stem[0]}'] = file_metrics()
            overall[dataset] = dataset_metrics()
        overall['aggregate'] = aggregate_metrics()

        n_params = 0
        for p in model.parameters():
            n_params += p.numel()
        overall['meta'] = {'n_params': n_params}

        # Write to json files
        directory = combnet.EVAL_DIR / combnet.CONFIG
        directory.mkdir(exist_ok=True, parents=True)
        with open(directory / 'overall.json', 'w') as file:
            json.dump(overall, file, indent=4)
        with open(directory / 'granular.json', 'w') as file:
            json.dump(granular, file, indent=4)

        print(overall)
