from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import gymnasium as gym
import numpy as np
import pandas as pd
import pytest
from dacbench.agents import StaticAgent
from dacbench.benchmarks import CMAESBenchmark, LubyBenchmark
from dacbench.logger import Logger, load_logs, log2dataframe
from dacbench.runner import run_benchmark
from dacbench.wrappers import ActionFrequencyWrapper


class TestActionTrackingWrapper(unittest.TestCase):
    def test_logging_multi_discrete(self):
        temp_dir = tempfile.TemporaryDirectory()

        seed = 0
        logger = Logger(
            output_path=Path(temp_dir.name),
            experiment_name="test_multi_discrete_logging",
            step_write_frequency=None,
            episode_write_frequency=1,
        )

        bench = CMAESBenchmark()
        bench.set_seed(seed)
        env = bench.get_environment()
        env.action_space.seed(seed)
        action_logger = logger.add_module(ActionFrequencyWrapper)
        wrapped = ActionFrequencyWrapper(env, logger=action_logger)
        action = env.action_space.sample()
        agent = StaticAgent(env, action)
        logger.set_env(env)

        run_benchmark(wrapped, agent, 1, logger)
        action_logger.close()

        logs = load_logs(action_logger.get_logfile())
        dataframe = log2dataframe(logs)

        expected_actions = pd.DataFrame(
            {
                f"{next(iter(action.keys()))}": [
                    action[next(iter(action.keys()))]
                ]
                * 10,
                f"{list(action.keys())[1]}": [action[list(action.keys())[1]]]
                * 10,
                f"{list(action.keys())[2]}": [action[list(action.keys())[2]]]
                * 10,
                f"{list(action.keys())[3]}": [action[list(action.keys())[3]]]
                * 10,
                f"{list(action.keys())[4]}": [action[list(action.keys())[4]]]
                * 10,
                f"{list(action.keys())[5]}": [action[list(action.keys())[5]]]
                * 10,
                f"{list(action.keys())[6]}": [action[list(action.keys())[6]]]
                * 10,
                f"{list(action.keys())[7]}": [action[list(action.keys())[7]]]
                * 10,
                f"{list(action.keys())[8]}": [action[list(action.keys())[8]]]
                * 10,
                f"{list(action.keys())[9]}": [action[list(action.keys())[9]]]
                * 10,
                f"{list(action.keys())[10]}": [action[list(action.keys())[10]]]
                * 10,
                f"{list(action.keys())[11]}_0": [action[list(action.keys())[11]]]
                * 10,
            }
        )
        
        for column in expected_actions.columns:
            self.assertListEqual(
                dataframe[column].to_list()[:10],
                expected_actions[column].to_list()[:10],
                f"Column  {column}",
            )

        temp_dir.cleanup()

    def test_logging_discrete(self):
        temp_dir = tempfile.TemporaryDirectory()

        seed = 0
        logger = Logger(
            output_path=Path(temp_dir.name),
            experiment_name="test_discrete_logging",
            step_write_frequency=None,
            episode_write_frequency=1,
        )

        bench = LubyBenchmark()
        bench.set_seed(seed)
        env = bench.get_environment()
        env.action_space.seed(seed)

        action_logger = logger.add_module(ActionFrequencyWrapper)
        wrapped = ActionFrequencyWrapper(env, logger=action_logger)
        action = env.action_space.sample()
        agent = StaticAgent(env, action)
        logger.set_env(env)

        run_benchmark(wrapped, agent, 10, logger)
        action_logger.close()

        logs = load_logs(action_logger.get_logfile())
        dataframe = log2dataframe(logs)

        expected_actions = [action] * 80

        self.assertListEqual(dataframe.action.to_list(), expected_actions)

        temp_dir.cleanup()

    def test_init(self):
        bench = LubyBenchmark()
        env = bench.get_environment()
        wrapped = ActionFrequencyWrapper(env)
        assert len(wrapped.overall_actions) == 0
        assert wrapped.action_interval is None
        wrapped.instance = [0]
        assert wrapped.instance[0] == 0

        wrapped2 = ActionFrequencyWrapper(env, 10)
        assert len(wrapped2.overall_actions) == 0
        assert wrapped2.action_interval == 10
        assert len(wrapped2.action_intervals) == 0
        assert len(wrapped2.current_actions) == 0

    def test_step(self):
        bench = LubyBenchmark()
        env = bench.get_environment()
        wrapped = ActionFrequencyWrapper(env, 10)

        state, info = wrapped.reset()
        assert issubclass(type(info), dict)
        assert len(state) > 1

        state, reward, terminated, truncated, _ = wrapped.step(1)
        assert len(state) > 1
        assert reward <= 0
        assert not terminated
        assert not truncated

        assert len(wrapped.overall_actions) == 1
        assert wrapped.overall_actions[0] == 1
        assert len(wrapped.current_actions) == 1
        assert wrapped.current_actions[0] == 1
        assert len(wrapped.action_intervals) == 0

    def test_get_actions(self):
        bench = LubyBenchmark()
        env = bench.get_environment()
        wrapped = ActionFrequencyWrapper(env)
        wrapped.reset()
        for i in range(5):
            wrapped.step(i)
        wrapped2 = ActionFrequencyWrapper(env, 2)
        wrapped2.reset()
        for i in range(5):
            wrapped2.step(i)

        overall_actions_only = wrapped.get_actions()
        overall_actions, intervals = wrapped2.get_actions()
        assert np.array_equal(overall_actions, overall_actions_only)
        assert overall_actions_only == [0, 1, 2, 3, 4]

        assert len(intervals) == 3
        assert len(intervals[0]) == 2
        assert intervals[0] == [0, 1]
        assert len(intervals[1]) == 2
        assert intervals[1] == [2, 3]
        assert len(intervals[2]) == 1
        assert intervals[2] == [4]

    def test_rendering(self):
        bench = LubyBenchmark()
        env = bench.get_environment()
        wrapped = ActionFrequencyWrapper(env, 2)
        wrapped.reset()
        wrapped.step(10)
        img = wrapped.render_action_tracking()
        assert img.shape[-1] == 3

        class dict_action_env:
            def __init__(self):
                self.action_space = gym.spaces.Dict(
                    {
                        "one": gym.spaces.Discrete(2),
                        "two": gym.spaces.Box(
                            low=np.array([-1, 1]), high=np.array([1, 5])
                        ),
                    }
                )
                self.observation_space = gym.spaces.Discrete(2)
                self.reward_range = (1, 2)
                self.metadata = {}

            def reset(self):
                return 1, {}

            def step(self, action):
                return 1, 1, 1, 1, {}

        env = dict_action_env()
        wrapped = ActionFrequencyWrapper(env)
        wrapped.reset()
        with pytest.raises(NotImplementedError):
            wrapped.render_action_tracking()

        class tuple_action_env:
            def __init__(self):
                self.action_space = gym.spaces.Tuple(
                    (
                        gym.spaces.Discrete(2),
                        gym.spaces.Box(low=np.array([-1, 1]), high=np.array([1, 5])),
                    )
                )
                self.observation_space = gym.spaces.Discrete(2)
                self.reward_range = (1, 2)
                self.metadata = {}

            def reset(self):
                return 1, {}

            def step(self, action):
                return 1, 1, 1, 1, {}

        env = tuple_action_env()
        wrapped = ActionFrequencyWrapper(env)
        wrapped.reset()
        with pytest.raises(NotImplementedError):
            wrapped.render_action_tracking()

        class multi_discrete_action_env:
            def __init__(self):
                self.action_space = gym.spaces.MultiDiscrete([2, 3])
                self.observation_space = gym.spaces.Discrete(2)
                self.reward_range = (1, 2)
                self.metadata = {}

            def reset(self):
                return 1, {}

            def step(self, action):
                return 1, 1, 1, 1, {}

        env = multi_discrete_action_env()
        wrapped = ActionFrequencyWrapper(env, 5)
        wrapped.reset()
        for _ in range(10):
            wrapped.step([1, 2])
        img = wrapped.render_action_tracking()
        assert img.shape[-1] == 3

        class multi_binary_action_env:
            def __init__(self):
                self.action_space = gym.spaces.MultiBinary(2)
                self.observation_space = gym.spaces.Discrete(2)
                self.reward_range = (1, 2)
                self.metadata = {}

            def reset(self):
                return 1, {}

            def step(self, action):
                return 1, 1, 1, 1, {}

        env = multi_binary_action_env()
        wrapped = ActionFrequencyWrapper(env)
        wrapped.reset()
        wrapped.step([1, 0])
        img = wrapped.render_action_tracking()
        assert img.shape[-1] == 3

        class large_action_env:
            def __init__(self):
                self.action_space = gym.spaces.Box(low=np.zeros(15), high=np.ones(15))
                self.observation_space = gym.spaces.Discrete(2)
                self.reward_range = (1, 2)
                self.metadata = {}

            def reset(self):
                return 1, {}

            def step(self, action):
                return 1, 1, 1, 1, {}

        env = large_action_env()
        wrapped = ActionFrequencyWrapper(env)
        wrapped.reset()
        wrapped.step(0.5 * np.ones(15))
        img = wrapped.render_action_tracking()
        assert img.shape[-1] == 3
