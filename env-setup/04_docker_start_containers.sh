#!/bin/bash

# stop if any error occur
set -e
source 00_vars.sh

echo "[[[Running 04.sh]]]"

sudo docker start $SHOPPING_CONTAINER_NAME
sudo docker start $SHOPPING_ADMIN_CONTAINER_NAME
sudo docker start $FORUM_CONTAINER_NAME
sudo docker start $GITLAB_CONTAINER_NAME
sudo docker start $WIKIPEDIA_CONTAINER_NAME

# cd openstreetmap-website/
# sudo docker compose start

echo -n -e "Waiting 60 seconds for all services to start..."
sleep 60

# GITLAB_STATUS=$(sudo docker inspect --format='{{json .State.Health.Status}}' $GITLAB_CONTAINER_NAME)
# echo "Gitlab status: $GITLAB_STATUS"
# echo -n -e " done\n"
