import os
import argparse

from agentlab.analyze.agent_xray import run_gradio, RESULTS_DIR

parser = argparse.ArgumentParser(
    description="Start the agent xray server.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "--results_dir",
    type=str,
    default=RESULTS_DIR,
    help="Directory to store results.",
)

parser.add_argument(
    "--port",
    type=int,
    default=21901,
    help="Port to run the server on.",
)

parser.add_argument(
    "--share",
    type=bool,
    default=False,
    help="Share the gradio server.",
    action=argparse.BooleanOptionalAction,
)

args = parser.parse_args()

if __name__ == "__main__":
    os.environ['AGENTXRAY_APP_PORT'] = str(args.port)
    os.environ['AGENTXRAY_SHARE_GRADIO'] = str(args.share).lower()

    run_gradio(args.results_dir)