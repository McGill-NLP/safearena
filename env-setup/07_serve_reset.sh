#!/bin/bash

# stop if any error occur
set -e


if [ "$HOST_WITH_CLOUDFLARE" = "true" ]; then
    export CF_TUNNEL_FOR_WEBARENA="true"
else
    export CF_TUNNEL_FOR_WEBARENA="false"
fi


source 00_vars.sh

echo "CUSTOM_INSTANCE_NUM in 07.sh: ${CUSTOM_INSTANCE_NUM}"
echo "INSTANCE_NUM in 07.sh: ${INSTANCE_NUM}"

# install flask in a venv
python3 -m venv venv_reset
source venv_reset/bin/activate

cd reset_server/

export CUSTOM_INSTANCE_NUM=${CUSTOM_INSTANCE_NUM}

python server.py --port ${RESET_PORT} 2>&1 | tee -a server.log
