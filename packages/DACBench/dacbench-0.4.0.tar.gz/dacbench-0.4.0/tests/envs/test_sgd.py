from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import numpy as np
import pytest
import torch
from dacbench import AbstractEnv
from dacbench.abstract_benchmark import objdict
from dacbench.benchmarks.sgd_benchmark import SGD_DEFAULTS, SGDBenchmark
from dacbench.envs.env_utils import sgd_utils
from dacbench.envs.sgd import SGDEnv, SGDInstance
from dacbench.wrappers import ObservationWrapper


class TestSGDEnv(unittest.TestCase):
    def make_env(self, epoch=True):
        bench = SGDBenchmark()
        bench.config.epoch_mode = epoch
        return bench.get_environment()

    @staticmethod
    def data_path(path):
        return os.path.join(os.path.dirname(__file__), "data", path)

    def test_setup(self):
        self.seed = 111
        bench = SGDBenchmark()
        bench.config.seed = self.seed
        env = bench.get_environment()
        assert issubclass(type(env), AbstractEnv)
        assert env.learning_rate is None
        assert env.initial_seed == self.seed
        assert isinstance(env.instance, SGDInstance)
        assert env.n_steps == SGD_DEFAULTS["cutoff"]

    def test_reward_function(self):
        def dummy_func(x):
            return 4 * x + 4

        benchmark = SGDBenchmark()
        benchmark.config = objdict(SGD_DEFAULTS.copy())
        benchmark.config["reward_function"] = dummy_func
        benchmark.read_instance_set()

        env = SGDEnv(benchmark.config)
        assert env.get_reward == dummy_func

        env2 = self.make_env()
        assert env2.get_reward == env2.get_default_reward

    def test_reset(self):
        env = self.make_env()
        state, info = env.reset()
        assert isinstance(state, dict)
        assert isinstance(info, dict)
        assert env.loss == 0
        assert env._done is False

    def test_step(self):
        env = self.make_env(False)
        state, info = env.reset()

        # Test if step method executes without error
        print(env.model)
        state, reward, done, truncated, info = env.step(0.001)
        assert isinstance(state, dict)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
        if not env._done:
            assert env.min_validation_loss is not None

        env = self.make_env()
        state, info = env.reset()

        # Test if step method executes without error in epoch mode
        state, reward, done, truncated, info = env.step(0.001)
        assert isinstance(state, dict)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
        if not env._done:
            assert env.min_validation_loss is not None

    def test_multiple_epochs(self):
        env = self.make_env()
        _ = env.reset()
        action = env.action_space.sample()
        for _ in range(5):
            _, reward, _, _, _ = env.step(action)
            assert reward > env.crash_penalty, "Env should not crash"

    def test_torch_hub_loading(self):
        bench = SGDBenchmark()
        env = bench.get_environment()
        env.instance_id_list = [0]
        env.instance_set = {0: env.instance_set[0]}
        env.instance_set[0].model = sgd_utils.load_model_from_torchhub(model_repo="chenyaofo/pytorch-cifar-models", model_name="cifar10_resnet20", pretrained=False)
        env.reset()
        assert env.model is not None
        assert env.model.__class__.__name__ == "Sequential"
        print(env.instance.dataset_name)
        env.step(0.001)

    def test_crash(self):
        with patch("dacbench.envs.sgd.forward_backward") as mock_forward_backward:
            mock_forward_backward.return_value = torch.tensor(float("inf"))
            env = ObservationWrapper(self.make_env())
            state, info = env.reset()

            state, reward, terminated, truncated, info = env.step(np.nan)
            assert env._done
            assert reward == env.crash_penalty
            assert not terminated
            assert truncated

    def test_reproducibility(self):
        mems = []
        instances = []
        env = self.make_env()

        for _ in range(2):
            rng = np.random.default_rng(123)
            env.seed(123)
            env.instance_index = 0
            instances.append(env.get_instance_set())

            state, info = env.reset()

            terminated, truncated = False, False
            mem = []
            step = 0
            while not (terminated or truncated) and step < 5:
                action = np.exp(rng.integers(low=-10, high=1))
                state, reward, terminated, truncated, _ = env.step(action)
                mem.append([state, [reward, int(truncated), action]])
                step += 1
            mems.append(mem)
        assert len(mems[0]) == len(mems[1])
        assert instances[0] == instances[1]

    def test_invalid_model(self):
        bench = SGDBenchmark()
        with pytest.raises(AttributeError):
            bench.config.layer_specification = [
                (
                    sgd_utils.LayerType.CONV2D,
                    {"in_channels": 1, "out_channels": 16, "kernel_size": 3},
                ),
                (sgd_utils.LayerType.POOLING, {"kernel_size": 2}),
                (sgd_utils.LayerType.FLATTEN, {}),
                (
                    sgd_utils.LayerType.LINEAR,
                    {"in_features": 16 * 13 * 13, "out_features": 128},
                ),
                (sgd_utils.LayerType.LINEAR, {"in_features": 128, "out_features": 10}),
                (sgd_utils.LayerType.LINEAR, {"in_features": 10, "out_features": 5}),
                (sgd_utils.LayerType.UNKOWN, {"in_features": 10, "out_features": 5}),
            ]

    def test_valid_model(self):
        bench = SGDBenchmark()
        bench.config.layer_specification = [
            (
                sgd_utils.LayerType.CONV2D,
                {"in_channels": 1, "out_channels": 16, "kernel_size": 3},
            ),
            (sgd_utils.LayerType.POOLING, {"kernel_size": 2}),
            (sgd_utils.LayerType.FLATTEN, {}),
            (
                sgd_utils.LayerType.LINEAR,
                {"in_features": 16 * 13 * 13, "out_features": 128},
            ),
            (sgd_utils.LayerType.LINEAR, {"in_features": 128, "out_features": 10}),
            (sgd_utils.LayerType.LINEAR, {"in_features": 10, "out_features": 5}),
        ]

    def test_close(self):
        env = self.make_env()
        assert env.close() is None

    def test_render(self):
        env = self.make_env()
        state, info = env.reset()
        env.render("human")
        with pytest.raises(NotImplementedError):
            env.render("random")
