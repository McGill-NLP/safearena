import argparse
import logging
import os
from pathlib import Path
from typing import List

from agentlab.agents.generic_agent.agent_configs import GenericAgentArgs
from agentlab.experiments.study import Study
from safearena import SafeArenaStudy, create_default_benchmark
from safearena.config import TASK_IDS
from safearena.modeling import (
    # prepare_qwen2, 
    # prepare_4o, 
    # prepare_llama_90b, 
    # prepare_llama_90b_together, 
    # prepare_qwen2_together, 
    # prepare_claude,
    prepare_gpt,
    prepare_vllm_model,
    prepare_claude,
    prepare_together,
)

logging.getLogger().setLevel(logging.INFO)


backbone_to_args = {
    "claude-3.5-sonnet": lambda: prepare_claude("anthropic/claude-3.5-sonnet-20240620"),
    "gpt-4o": lambda: prepare_gpt("gpt-4o-2024-11-20"),
    "gpt-4o-mini": lambda: prepare_gpt("gpt-4o-mini-2024-07-18"),
    "llama-3.2-90b": lambda: prepare_vllm_model("meta-llama/Llama-3.2-90B-Vision-Instruct"),
    "llama-3.2-90b-together": lambda: prepare_together("meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"),
    "llama-3.3-70b": lambda: prepare_vllm_model("meta-llama/Llama-3.3-70B-Instruct", use_vision=False),
    "qwen-2-vl-72b": lambda: prepare_vllm_model("Qwen/Qwen2-VL-72B-Instruct"),
    "qwen-2.5-vl-72b": lambda: prepare_vllm_model("Qwen/Qwen2.5-VL-72B-Instruct"),
}

def run_experiment(backbones, n_jobs, suffix, relaunch, reproduce, benchmark, parallel="sequential"):
    # if relaunch:
    #     #  relaunch an existing study
    #     study = SafeArenaStudy.load_most_recent(contains=contains)
    #     study.find_incomplete(include_errors=True)
    # else: 
    #     study = SafeArenaStudy(
    #         single_agent_args=agent_args,
    #         suffix= suffix,
    #         benchmark=benchmark
    #     )
    agent_args: List[GenericAgentArgs] = []

    for backbone in backbones:
        if backbone not in backbone_to_args:
            raise ValueError(f"Backbone {backbone} not found in available backbones: {list(backbone_to_args.keys())}")
        agent_args.append(backbone_to_args[backbone]())

    if relaunch is not None:
        print("Relaunching study from directory containing:", relaunch)
        study = Study.load_most_recent(contains=relaunch, root_dir=Path(os.environ["AGENTLAB_EXP_ROOT"]))
        study.find_incomplete(include_errors=True)
    else:
        study = Study(agent_args, benchmark, logging_level_stdout=logging.INFO, suffix=suffix)  # type: ignore

    if reproduce:
        [a.set_reproducibility_mode() for a in agent_args]
    
    study.run(
        n_jobs=n_jobs,
        parallel_backend=parallel,
        strict_reproducibility=False,
        n_relaunch=3,
    )


if __name__ == "__main__":  # necessary for dask backend
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-b",
        "--backbones",
        type=str,
        default="4o-mini",
        # allow multiple backbones
        nargs="+",
        choices=list(backbone_to_args.keys()),
    )
    parser.add_argument(
        "-n",
        "--n_jobs",
        type=int,
        default=1,
        help="""Number of jobs to run experiments. Defaults to : 1.""",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="",
        help="""Suffix for experiment name. Defaults to : None.""",
    )
    parser.add_argument(
        "--reproduce",
        type=bool,
        default=False,
        help="""Bool for reproducibility mode. Defaults to : False""",
        action=argparse.BooleanOptionalAction,
    )
    # parser.add_argument(
    #     "--relaunch",
    #     type=bool,
    #     default=False,
    #     help="""Bool value for relaunch". Defaults to false""",
    #     action=argparse.BooleanOptionalAction,
    # )
    # parser.add_argument(
    #     "--contains",
    #     type=str,
    #     default=None,
    #     help="""Keyword to find exp dir if relaunch is set to true. Defaults to empty""",
    # )
    parser.add_argument(
        "--relaunch",
        type=str,
        default=None,
        help="""Keyword to find exp dir if relaunch is set to true. Defaults to empty""",
    )
    parser.add_argument(
        "--parallel",
        type=str,
        default="sequential",
        help="""Parallel backend to use. Defaults to : sequential.""",
        choices=["sequential", "ray", "joblib"],
    )

    args, unknown = parser.parse_known_args()

    # if args.contains == None and args.relaunch == True:
    #     raise Exception("Value contains is set to None but relaunch is true. You must provide a keyword to find the experiment directory")
    
    # if args.contains != None:
    #     if args.contains == True:
    #         raise Exception("Value contains is set to not None but relaunch is false")
    
    # if args.backbone == "4o-mini":
    #     backbone_agent_arg = prepare_4o(model_name = "gpt-4o-mini-2024-07-18")
    # elif args.backbone == "4o":
    #     backbone_agent_arg = prepare_4o(model_name="gpt-4o-2024-11-20")
    # elif args.backbone == "llama-3.2-vllm":
    #     backbone_agent_arg = prepare_llama_90b()
    # elif args.backbone == "llama-3.2-together":
    #     backbone_agent_arg = prepare_llama_90b_together()
    # elif args.backbone == "qwen-2-vllm":
    #     backbone_agent_arg = prepare_qwen2()
    # elif args.backbone == "qwen-2-together":
    #     backbone_agent_arg = prepare_qwen2_together()
    # elif args.backbone == "claude-3.5-sonnet":
    #     backbone_agent_arg = prepare_claude()
    # else:
    #     raise Exception("Backbone not found")

    benchmark = create_default_benchmark(task_ids=TASK_IDS)

    run_experiment(
        backbones=args.backbones,
        n_jobs=args.n_jobs,
        suffix=args.suffix,
        relaunch=args.relaunch,
        reproduce=args.reproduce,
        benchmark=benchmark,
        parallel=args.parallel,
    )
