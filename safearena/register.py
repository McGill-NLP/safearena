import logging

from browsergym.core.registration import register_task

from . import config, task

logger = logging.getLogger(__name__)
ALL_SAFEARENA_TASK_IDS = []


# register all SafeArena benchmark
for task_id in config.TASK_IDS:
    gym_id = f"safearena.{task_id}"
    register_task(
        gym_id,
        task.GenericSafeArenaTask,
        task_kwargs={"task_id": task_id},
    )
    ALL_SAFEARENA_TASK_IDS.append(gym_id)
    logger.debug(f"Registered task {gym_id} out of a total of {len(ALL_SAFEARENA_TASK_IDS)} tasks")
    logger.debug(f"Last 5 SafeArena tasks: {ALL_SAFEARENA_TASK_IDS[-5:]}")

logger.info(f"Registered a total of {len(ALL_SAFEARENA_TASK_IDS)} SafeArena tasks. The first 5 tasks are: {ALL_SAFEARENA_TASK_IDS[:5]}")