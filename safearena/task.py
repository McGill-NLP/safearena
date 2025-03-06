import importlib.resources
import json
import logging
from pathlib import Path
from typing import Optional
import playwright.sync_api
from browsergym.webarena.task import GenericWebArenaTask, AbstractBrowserTask

from .config import all_configs_str_raw

logger = logging.getLogger(__name__)

def infer_task_type(task_id: str) -> str:
    task_type = task_id.split(".", 1)
    if len(task_type) != 2:
        raise ValueError(f"Invalid task_id format: {task_id}. It must be prefixed with 'safe' or 'harm'.")
    return task_type[0]

class GenericSafeArenaTask(GenericWebArenaTask):
    def __init__(
        self,
        seed: int,
        task_id: Optional[int] = None,
        intent_template_id: Optional[int] = None,
        with_na_hint: bool = False,
        with_homepage_hint: bool = False,
    ) -> None:
        from browsergym.webarena.instance import WebArenaInstance

        super(GenericWebArenaTask, self).__init__(seed)

        # task properties, will be used to set up the browsergym environment
        self.viewport = {"width": 1280, "height": 720}
        self.slow_mo = 1000  # ms
        self.timeout = 10000  # ms

        self.webarena_instance = WebArenaInstance()
        self.config_file: str = None
        self.with_na_hint = with_na_hint
        self.with_homepage_hint = with_homepage_hint

        # one and only one of task id and template id must be provided
        if (task_id is None) == (intent_template_id is None):
            raise ValueError(
                f"One and only one of 'task_id' and 'intent_template_id' must be provided (task_id={task_id}, intent_template_id={intent_template_id})."
            )

        # read the list of all webarena task configs
        from safearena.config import all_configs_raw_dict

        combined_configs = all_configs_raw_dict["safe"] + all_configs_raw_dict["harm"]

        all_configs_str = json.dumps(combined_configs)

        # substitute URLs
        for pattern, url_key in {
            "__GITLAB__": "gitlab",
            "__REDDIT__": "reddit",
            "__SHOPPING__": "shopping",
            "__SHOPPING_ADMIN__": "shopping_admin",
            "__WIKIPEDIA__": "wikipedia",
            "__MAP__": "map",
        }.items():
            all_configs_str = all_configs_str.replace(pattern, self.webarena_instance.urls[url_key])

        # load all task configs to JSON
        all_configs = json.loads(all_configs_str)

        # keep only the desired task configs
        if intent_template_id is not None:
            raise NotImplementedError("intent_template_id is not supported yet.")
            # task_configs = [
            #     conf for conf in all_configs if conf["intent_template_id"] == intent_template_id
            # ]
            # if not task_configs:
            #     raise ValueError(
            #         f"Could not find any task config with intent_template_id={intent_template_id}."
            #     )

        elif task_id is not None:
            task_configs = [conf for conf in all_configs if conf["task_id"] == task_id]
            if not task_configs:
                raise ValueError(
                    f"Could not find any task config with task_id={task_id}."
                )

        self.task_configs = task_configs
    
    def setup(self, page: playwright.sync_api.Page) -> tuple[str, dict]:
        # register task on import
        from .helper.evaluators import safearena_eval_router

        goal, d = super().setup(page)

        if self.config_file is None:
            raise ValueError("Config file not set by GenericSafeArenaTask.setup(). Please set it in the derived class.")

        # we patch the router to use our own evaluator router
        self.evaluator = safearena_eval_router(self.config_file)

        return goal, d
