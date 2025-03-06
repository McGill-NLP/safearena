import json
import os


_task_env_var = os.getenv("SAFEARENA_TASK", "harm")
safearena_data_dir = os.getenv("SAFEARENA_DATA_DIR", "data")

all_configs_raw_dict = {}
for option in ['harm', 'safe']:
    data_path = os.path.join(safearena_data_dir, f'{option}.json')

    if os.path.exists(data_path) is False:
        raise FileNotFoundError(f"File {data_path} not found. Please download the data file from the SafeArena dataset repository and place them in the data/ directory.")

    with open(data_path, 'r') as fp:
        all_configs_str_raw = fp.read()

    all_configs_raw_dict[option] = json.loads(all_configs_str_raw)

SAFE_TASK_IDS = [conf["task_id"] for conf in all_configs_raw_dict["safe"]]
HARM_TASK_IDS = [conf["task_id"] for conf in all_configs_raw_dict["harm"]]
TASK_IDS = SAFE_TASK_IDS + HARM_TASK_IDS
