"""Utils for the environments."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data.dataloader import DataLoader
from torchvision import datasets, transforms

datasets.CIFAR10.download  # noqa: B018


DATASETS = {
    "MNIST": {
        "train_transform": transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
        ),
        "test_transform": transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
        ),
        "icgen_name": "mnist",
    },
    "CIFAR10": {
        "train_transform": transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ]
        ),
        "test_transform": transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ]
        ),
        "icgen_name": "cifar10",
    },
    "FashionMNIST": {
        "train_transform": transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))]
        ),
        "test_transform": transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))]
        ),
        "icgen_name": "fashion_mnist",
    },
}


def random_torchvision_loader(
    seed: int,
    dataset_path: str,
    name: str | None,
    batch_size: int,
    fraction_of_dataset: float,
    train_validation_ratio: float | None,
    dataset_config: dict | None = None,
    **kwargs,
) -> tuple[DataLoader, DataLoader, DataLoader]:
    """Create train, validation, test loaders for `name` dataset."""
    rng = np.random.RandomState(seed)

    if dataset_config is None:
        dataset_config = DATASETS.copy()

    if name is None:
        rng.seed(seed)
        name = rng.choice(np.array(list(datasets.keys())))

    if train_validation_ratio is None:
        train_validation_ratio = (
            1 - int(np.exp(rng.uniform(low=np.log(5), high=np.log(20)))) / 100
        )

    train_transform = dataset_config[name]["train_transform"]
    test_transform = dataset_config[name]["test_transform"]

    train_dataset = getattr(datasets, name)(
        dataset_path, train=True, download=True, transform=train_transform
    )
    train_size = int(len(train_dataset) * fraction_of_dataset)
    test = getattr(datasets, name)(dataset_path, train=False, transform=test_transform)
    train_size = int(len(train_dataset) * train_validation_ratio)
    train_size = train_size - train_size % batch_size
    train, val = torch.utils.data.random_split(
        train_dataset, [train_size, len(train_dataset) - train_size]
    )
    train_loader = DataLoader(
        train, batch_size=batch_size, drop_last=True, shuffle=True
    )
    val_loader = DataLoader(val, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test, batch_size=64)
    return (train_dataset, test), (train_loader, val_loader, test_loader)


def random_instance(rng: np.random.RandomState, datasets):
    """Samples a random Instance."""
    default_rng_state = torch.get_rng_state()
    seed = rng.randint(1, 4294967295, dtype=np.int64)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    instance = _random_instance(rng, datasets)
    torch.set_rng_state(default_rng_state)
    return instance


def _random_instance(
    rng: np.random.RandomState,
    datasets,
    **kwargs,
):
    """Helper for samling a random instance."""
    batch_size = 2 ** int(np.exp(rng.uniform(low=np.log(4), high=np.log(8))))

    model = random_architecture(rng, datasets[0][0][0].shape, len(datasets[0].classes))
    optimizer_params = sample_optimizer_params(rng, **kwargs)

    crash_penalty = np.log(len(datasets[0].classes))
    return (
        model,
        optimizer_params,
        batch_size,
        crash_penalty,
    )


def sample_optimizer_params(rng, **kwargs):
    """Samples optimizer parameters according to below rules.
    -With 0.8 probability keep default of all parameters
    -For each hyperparameter, with 0.5 probability sample a new value else keep default.
    """
    modify = rng.rand()

    weight_decay = (
        np.exp(rng.uniform(low=np.log(1e-6), high=np.log(0.1)))
        if modify > 0.8 and rng.rand() > 0.5
        else 1e-2
    )

    eps = (
        np.exp(rng.uniform(low=np.log(1e-10), high=np.log(1e-6)))
        if modify > 0.8 and rng.rand() > 0.5
        else 1e-8
    )

    beta1 = 1 - (
        np.exp(rng.uniform(low=np.log(0.0001), high=np.log(0.2)))
        if modify > 0.8 and rng.rand() > 0.5
        else 0.1
    )

    beta2 = 1 - (
        np.exp(rng.uniform(low=np.log(0.0001), high=np.log(0.2)))
        if modify > 0.8 and rng.rand() > 0.5
        else 0.0001
    )

    return {
        "weight_decay": weight_decay,
        "eps": eps,
        "betas": (beta1, beta2),
    }


def random_architecture(
    rng: np.random.RandomState,
    input_shape: tuple[int, int, int],
    n_classes: int,
) -> nn.Module:
    """Samples random architecture with `rng` for given `input_shape`
    and `n_classes`.
    """
    modules = [nn.Identity()]
    max_n_conv_layers = 3
    n_conv_layers = rng.randint(low=0, high=max_n_conv_layers + 1)
    prev_conv = input_shape[0]
    kernel_sizes = [3, 5, 7][: max(0, 3 - n_conv_layers + 1)]
    activation = rng.choice([nn.Identity, nn.ReLU, nn.PReLU, nn.ELU])
    batch_norm_2d = rng.choice([nn.Identity, nn.BatchNorm2d])
    bn_first = rng.choice([False, True])

    for layer_idx, layer_exp in enumerate(range(1, int(n_conv_layers * 2 + 1), 2)):
        if layer_idx > 0:
            modules.append(nn.MaxPool2d(2))
        conv = int(
            np.exp(
                rng.uniform(low=np.log(2**layer_exp), high=np.log(2 ** (layer_exp + 2)))
            )
        )
        kernel_size = rng.choice(kernel_sizes)
        modules.append(nn.Conv2d(prev_conv, conv, kernel_size, 1))
        prev_conv = conv
        if bn_first:
            modules.append(batch_norm_2d(prev_conv))
        modules.append(activation())
        if not bn_first:
            modules.append(batch_norm_2d(prev_conv))

    feature_extractor = nn.Sequential(*modules)

    linear_layers = [nn.Flatten()]
    batch_norm_1d = rng.choice([nn.Identity, nn.BatchNorm1d])
    max_n_mlp_layers = 2
    n_mlp_layers = int(rng.randint(low=0, high=max_n_mlp_layers + 1))
    prev_l = int(
        torch.prod(
            torch.tensor(feature_extractor(torch.zeros((1, *input_shape))).shape)
        ).item()
    )
    for layer_idx in range(n_mlp_layers):
        l = 2 ** (  # noqa: E741
            2 ** (max_n_mlp_layers + 1 - layer_idx)
            - int(
                np.exp(
                    rng.uniform(
                        low=np.log(1), high=np.log(max_n_mlp_layers + 1 + layer_idx)
                    )
                )
            )
        )
        linear_layers.append(nn.Linear(prev_l, l))
        prev_l = l
        if bn_first:
            linear_layers.append(batch_norm_1d(prev_l))
        linear_layers.append(activation())
        if not bn_first:
            linear_layers.append(batch_norm_1d(prev_l))

    linear_layers.append(nn.Linear(prev_l, n_classes))
    linear_layers.append(nn.LogSoftmax(1))
    mlp = nn.Sequential(*linear_layers)
    return nn.Sequential(feature_extractor, mlp)


class LayerType:
    """Enum for supported torch layers."""

    CONV2D = "CONV2D"
    LINEAR = "LINEAR"
    FLATTEN = "FLATTEN"
    POOLING = "POOLING"
    DROPOUT = "DROPOUT"
    RELU = "RELU"
    LOGSOFTMAX = "LOGSOFTMAX"


# Define a mapping from layer type to the corresponding PyTorch module
layer_mapping = {
    LayerType.CONV2D: nn.Conv2d,
    LayerType.LINEAR: nn.Linear,
    LayerType.FLATTEN: nn.Flatten,
    LayerType.POOLING: nn.MaxPool2d,
    LayerType.DROPOUT: nn.Dropout,
    LayerType.RELU: nn.ReLU,
    LayerType.LOGSOFTMAX: nn.LogSoftmax,
}


# Define a function to create the model based on the layer specification
def create_model_from_layer_description(model_description_file) -> nn.Sequential:
    """Creates a torch model using the given layer_specification.

    Returns:
        nn.Sequential: The pytorch model
    """
    dacbench_path = (
        Path(__file__).resolve().parent
        / "../../instance_sets/sgd/"
        / model_description_file
    )
    if Path(model_description_file).exists():
        with open(model_description_file) as f:
            layer_specification = json.load(f)
    elif dacbench_path.exists():
        with open(dacbench_path) as f:
            layer_specification = json.load(f)
    else:
        raise FileNotFoundError(f"File {model_description_file} not found.")

    def make_model():
        layers = []
        for layer_type, layer_params in layer_specification:
            layer_class = layer_mapping[layer_type]
            layer = layer_class(**layer_params)
            layers.append(layer)
        return nn.Sequential(*layers)

    return make_model


def load_model_from_torchhub(
    model_repo: str, model_name: str, pretrained: bool, local: bool | str = False
):
    """Loads a model from torchhub."""

    def make_model():
        local_kwargs = {}
        model_loc = model_repo
        if local:
            local_kwargs["source"] = "local"
            model_loc = local
        hub_model = torch.hub.load(
            model_loc, model_name, pretrained=bool(pretrained), **local_kwargs
        )
        return torch.nn.Sequential(hub_model, torch.nn.LogSoftmax(dim=0))

    return make_model


def get_model_constructor(model_type, model_kwargs, local=False):
    """Get the model constructor based on the model type."""
    if model_type == "from_file":
        return create_model_from_layer_description(*model_kwargs)
    elif model_type == "from_torchhub":  # noqa: RET505
        return load_model_from_torchhub(*model_kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
