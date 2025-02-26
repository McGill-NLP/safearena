#!/bin/bash

# stop if any error occur
set -e

if [ "$HOST_WITH_CLOUDFLARE" = "true" ]; then
    export GITLAB_INTERNAL_PORT=443
    source 00cf_vars.sh
else
    export GITLAB_INTERNAL_PORT=$GITLAB_PORT
    source 00_vars.sh
fi


echo "Running 03.sh"

WORKING_DIR=$(pwd)

sudo docker create --name $SHOPPING_CONTAINER_NAME -p $SHOPPING_PORT:80 shopping_final_0712
sudo docker create --name $SHOPPING_ADMIN_CONTAINER_NAME -p $SHOPPING_ADMIN_PORT:80 safearena_shopping_admin
sudo docker create --name $FORUM_CONTAINER_NAME -p $REDDIT_PORT:80 safearena_forum
sudo docker create --name $GITLAB_CONTAINER_NAME -p $GITLAB_PORT:$GITLAB_INTERNAL_PORT safearena_gitlab /opt/gitlab/embedded/bin/runsvdir-start --env GITLAB_PORT=$GITLAB_INTERNAL_PORT
sudo docker create --name $WIKIPEDIA_CONTAINER_NAME --volume=${WORKING_DIR}/containers:/data -p $WIKIPEDIA_PORT:80 ghcr.io/kiwix/kiwix-serve:3.3.0 wikipedia_en_all_maxi_2022-05.zim
