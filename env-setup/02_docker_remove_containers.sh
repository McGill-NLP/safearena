#!/bin/bash

# stop if any error occur
set -e
source 00_vars.sh

echo "[[[Running 02.sh]]]"

#  || true is used to ignore errors if the container is not found
sudo docker stop $SHOPPING_ADMIN_CONTAINER_NAME $FORUM_CONTAINER_NAME $GITLAB_CONTAINER_NAME $SHOPPING_CONTAINER_NAME $WIKIPEDIA_CONTAINER_NAME || true
sudo docker remove $SHOPPING_ADMIN_CONTAINER_NAME $FORUM_CONTAINER_NAME $GITLAB_CONTAINER_NAME $SHOPPING_CONTAINER_NAME $WIKIPEDIA_CONTAINER_NAME || true

