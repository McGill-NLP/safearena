import logging
import os
from slugify import slugify

import nltk
from agentlab.agents.agent_args import AgentArgs
from agentlab.agents.generic_agent.agent_configs import GenericAgentArgs
from agentlab.experiments import reproducibility_util as repro
from agentlab.experiments.study import Study

import bgym
from bgym import ExpArgs
from browsergym.experiments.benchmark import HighLevelActionSetArgs
from browsergym.experiments.loop import EnvArgs
from browsergym.experiments.benchmark.utils import (
    make_env_args_list_from_fixed_seeds
)

from browsergym.experiments.benchmark import Benchmark
from browsergym.experiments.benchmark.utils import massage_tasks
from browsergym.webarena.instance import WebArenaInstance

from . import config, task

try:
    nltk.data.find("tokenizers/punkt_tab")
except:
    nltk.download("punkt_tab", quiet=True, raise_on_error=True)

logger = logging.getLogger(__name__)


class ModifiedEnvArgs(EnvArgs):
    def make_env(self, action_mapping, exp_dir, exp_task_kwargs: dict = {}):
        from . import register

        return super().make_env(action_mapping, exp_dir, exp_task_kwargs)
    
def modified_make_env_args_list_from_fixed_seeds(
    task_list: list[str], max_steps: int, fixed_seeds: list[int]
):
    """
    Generates a list of `len(task_list)` time `n_repeats` environments arguments, using randomly generated seeds.
    """
    env_args_list = []
    for task in task_list:
        for seed in fixed_seeds:
            env_args_list.append(
                ModifiedEnvArgs(
                    task_name=task,
                    task_seed=int(seed),
                    max_steps=max_steps,
                    headless=True,
                    record_video=False,
                    wait_for_user_message=False,
                    viewport=None,
                    slow_mo=None,
                    storage_state=None,
                    task_kwargs=None,
                )
            )

    return env_args_list


class SafeArenaInstance(WebArenaInstance):
    def __init__(self):
        super().__init__()

        # remove wikipedia and map from the self.urls (dict) since we don't use them in safearena
        self.urls.pop("wikipedia")
        self.urls.pop("map")


class SafeArenaBenchmark(Benchmark):
    # overwrite backends
    logger = logging.getLogger(__name__)

    def prepare_backends(self):
        from . import register

        self.logger.info(f"Preparing SafeArena backend...")
        default_instance = SafeArenaInstance()

        if os.getenv("SAFEARENA_DISABLE_FULL_RESET", "").lower() not in ['true', '1']:
            default_instance.full_reset()
        else:
            logger.warning(f"Full reset disabled. Will not reset the instance. Please ensure the instance is clean.")
        
        if os.getenv("SAFEARENA_DISABLE_MASSAGE", "").lower() not in ['true', '1']:
            # get the first, last and middle task of config.TASK_IDS
            massage_tasks([f"safearena.{id}" for id in [config.TASK_IDS[0], config.TASK_IDS[-1], config.TASK_IDS[len(config.TASK_IDS)//2]]])
        else:
            logger.warning(f"Massage tasks disabled. Please ensure the tasks are functional.")
        
        self.logger.info(f"SafeArena backend ready")

    def get_version(self):
        from .version import __version__

        return __version__


def create_default_benchmark(task_ids, name="safearena"):
    benchmark = SafeArenaBenchmark(
        name=name,
        high_level_action_set_args=HighLevelActionSetArgs(
            subsets=["webarena"],
            multiaction=False,
            strict=False,
            retry_with_force=True,
            demo_mode="off",
        ),
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=[],  # doesn't matter what we put here, since we overwrite prepare_backends
        env_args_list=modified_make_env_args_list_from_fixed_seeds(
            task_list=[f"safearena.{i}" for i in task_ids],
            max_steps=30,
            fixed_seeds=[0],
        ),
    )

    return benchmark

