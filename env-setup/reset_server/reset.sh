#!/bin/bash

# stop if any error occur
set -e

cd ..

echo "CUSTOM_INSTANCE_NUM: ${CUSTOM_INSTANCE_NUM}"

export CUSTOM_INSTANCE_NUM=${CUSTOM_INSTANCE_NUM}

echo "{
  \"status\": \"step 0/4 complete\"
}" > reset_server/reset-status-$CUSTOM_INSTANCE_NUM.json

bash 02_docker_remove_containers.sh > reset_server/reset-logs-$CUSTOM_INSTANCE_NUM.txt
# write status to reset-status.json
echo "{
  \"status\": \"step 1/4 complete\"
}" > reset_server/reset-status-$CUSTOM_INSTANCE_NUM.json

bash 03_docker_create_containers.sh >> reset_server/reset-logs-$CUSTOM_INSTANCE_NUM.txt

# write status to reset-status.json

echo "{
  \"status\": \"step 2/4 complete\"
}" > reset_server/reset-status-$CUSTOM_INSTANCE_NUM.json

bash 04_docker_start_containers.sh >> reset_server/reset-logs-$CUSTOM_INSTANCE_NUM.txt

# write status to reset-status.json
echo "{
  \"status\": \"step 3/4 complete\"
}" > reset_server/reset-status-$CUSTOM_INSTANCE_NUM.json

bash 05_docker_patch_containers.sh >> reset_server/reset-logs-$CUSTOM_INSTANCE_NUM.txt

# delete reset-status.json only if the file exists
rm -f reset_server/reset-status-$CUSTOM_INSTANCE_NUM.json