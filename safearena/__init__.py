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




# Existing Study object requires reproducibility info; we overwrite temporarily (also raises unknown benchmark error otherwise)
class SafeArenaStudy(Study):
    def __init__(
        self, single_agent_args: GenericAgentArgs, benchmark, suffix=None, 
    ):
        self.single_agent_args = single_agent_args
        self.benchmark = benchmark
        self.suffix = suffix

        super().__init__(agent_args=[single_agent_args], benchmark=benchmark, suffix=suffix)

    @property
    def name(self):
        _task_env_var = os.getenv("SAFEARENA_TASK", "unknown_task")
        study_name = f"{self.agent_args[0].agent_name}_on_{self.benchmark.name}_{_task_env_var}"

        if self.suffix:
            study_name += f"_{self.suffix}"
        
        study_name = slugify(study_name, max_length=500, allow_unicode=True)

        return study_name


    def make_exp_args_list(self):
        self.exp_args_list = self._agent_on_benchmark_(
            single_agent_args=self.single_agent_args,
            benchmark=self.benchmark,
        )
        return self.exp_args_list
    
    
    def set_reproducibility_info(self, strict_reproducibility=False, comment=None):
        """Gather relevant information that may affect the reproducibility of the experiment

        e.g.: versions of BrowserGym, benchmark, AgentLab..."""
        agent_names = [a.agent_name for a in self.agent_args]
        info = repro.get_reproducibility_info(
            agent_names,
            self.benchmark,
            self.uuid,
            ignore_changes=not strict_reproducibility,
            comment=comment,
        )
        if self.reproducibility_info is not None:
            repro.assert_compatible(
                self.reproducibility_info, info, raise_if_incompatible=strict_reproducibility
            )
        self.reproducibility_info = info
    
    

    def _agent_on_benchmark_(
        self,
        benchmark: bgym.Benchmark,
        single_agent_args: AgentArgs = None,
        demo_mode=False,
        logging_level: int = logging.INFO,
        logging_level_stdout: int = logging.INFO,
    ):

        env_args_list = benchmark.env_args_list
        exp_args_list = []
        for env_args in env_args_list:
            single_agent_args.set_benchmark(benchmark, demo_mode=demo_mode)
            exp_args = ExpArgs(
                agent_args=single_agent_args,
                env_args=env_args,
                logging_level=logging_level,
                logging_level_stdout=logging_level_stdout,
            )

            exp_args_list.append(exp_args)

        for i, exp_args in enumerate(exp_args_list):
            exp_args.order = i
        
        return exp_args_list




def create_default_benchmark(task_ids):
    benchmark = SafeArenaBenchmark(
        name="safearena",
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

