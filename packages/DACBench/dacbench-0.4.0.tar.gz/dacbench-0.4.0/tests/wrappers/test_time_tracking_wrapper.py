from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
from dacbench.agents import StaticAgent
from dacbench.benchmarks import LubyBenchmark
from dacbench.logger import Logger, load_logs, log2dataframe
from dacbench.runner import run_benchmark
from dacbench.wrappers import EpisodeTimeWrapper


class TestTimeTrackingWrapper(unittest.TestCase):
    def test_logging(self):
        temp_dir = tempfile.TemporaryDirectory()

        episodes = 5
        logger = Logger(
            output_path=Path(temp_dir.name),
            experiment_name="test_logging",
        )
        bench = LubyBenchmark()
        env = bench.get_environment()
        time_logger = logger.add_module(EpisodeTimeWrapper)
        wrapped = EpisodeTimeWrapper(env, logger=time_logger)
        agent = StaticAgent(env=env, action=1)
        run_benchmark(wrapped, agent, episodes, logger)

        logger.close()

        logs = load_logs(time_logger.get_logfile())
        dataframe = log2dataframe(logs)

        # all steps must have logged time
        assert (~dataframe.step_duration.isna()).any()
        # each episode has a recored time
        assert (~dataframe.episode_duration.isna()).all()

        temp_dir.cleanup()

    def test_init(self):
        bench = LubyBenchmark()
        env = bench.get_environment()
        wrapped = EpisodeTimeWrapper(env)
        assert len(wrapped.overall_times) == 0
        assert wrapped.time_interval is None
        wrapped.instance = [0]
        assert wrapped.instance[0] == 0

        wrapped2 = EpisodeTimeWrapper(env, 10)
        assert len(wrapped2.overall_times) == 0
        assert wrapped2.time_interval == 10
        assert len(wrapped2.time_intervals) == 0
        assert len(wrapped2.current_times) == 0

    def test_step(self):
        bench = LubyBenchmark()
        env = bench.get_environment()
        wrapped = EpisodeTimeWrapper(env, 10)

        state, info = wrapped.reset()
        assert issubclass(type(info), dict)
        assert len(state) > 1

        state, reward, terminated, truncated, _ = wrapped.step(1)
        assert len(state) > 1
        assert reward <= 0
        assert not terminated
        assert not truncated

        assert len(wrapped.all_steps) == 1
        assert len(wrapped.current_step_interval) == 1
        assert len(wrapped.step_intervals) == 0

        for _ in range(20):
            wrapped.step(1)

        assert len(wrapped.overall_times) > 2
        assert len(wrapped.time_intervals) == 1

    def test_get_times(self):
        bench = LubyBenchmark()
        env = bench.get_environment()
        wrapped = EpisodeTimeWrapper(env)
        wrapped.reset()
        for i in range(5):
            wrapped.step(i)
        wrapped2 = EpisodeTimeWrapper(env, 2)
        wrapped2.reset()
        for i in range(5):
            wrapped2.step(i)

        overall_times_only, steps_only = wrapped.get_times()
        overall_times, steps, intervals, step_intervals = wrapped2.get_times()
        assert np.array_equal(
            np.round(overall_times, decimals=2),
            np.round(overall_times_only, decimals=2),
        )
        assert len(step_intervals) == 3
        assert len(step_intervals[0]) == 2
        assert len(step_intervals[1]) == 2
        assert len(step_intervals[2]) == 1

    def test_rendering(self):
        bench = LubyBenchmark()
        env = bench.get_environment()
        wrapped = EpisodeTimeWrapper(env, 10)
        wrapped.reset()
        for _ in range(30):
            wrapped.step(1)
        img = wrapped.render_step_time()
        assert img.shape[-1] == 3
        img = wrapped.render_episode_time()
        assert img.shape[-1] == 3
