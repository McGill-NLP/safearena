import json
import os


_task_env_var = os.getenv("SAFEARENA_TASK", "harm")
safearena_data_dir = os.getenv("SAFEARENA_DATA_DIR", "data")

if _task_env_var == "harm":
    data_path = os.path.join(safearena_data_dir, 'harm.json')
elif _task_env_var == "safe":
    data_path = os.path.join(safearena_data_dir, 'safe.json')
else:
    raise ValueError("SAFEARENA_TASK environment variable not set to harm or safe")

if os.path.exists(data_path) is False:
    raise FileNotFoundError(f"File {data_path} not found. Please download the data file from the SafeArena dataset repository and place them in the data/ directory.")

with open(data_path, 'r') as fp:
    all_configs_str_raw = fp.read()

all_configs_raw_dict = json.loads(all_configs_str_raw)

# Those should be numerical values, e.g. 0,1,2,3... not the actual task names, e.g. safearena.0, safearena.1, safearena.2...
TASK_IDS = [conf["task_id"] for conf in all_configs_raw_dict]
