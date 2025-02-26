#!/bin/bash

# stop if any error occur
set -e

source 00_vars.sh

echo "Running 01.sh"

assert() {
  if ! "$@"; then
    echo "Assertion failed: $@" >&2
    exit 1
  fi
}

load_docker_image() {
  local IMAGE_NAME="$1"
  local INPUT_FILE="$2"

  if ! sudo docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${IMAGE_NAME}:"; then
    echo "Loading Docker image ${IMAGE_NAME} from ${INPUT_FILE}"
    sudo docker load --input "${INPUT_FILE}"
  else
    echo "Docker image ${IMAGE_NAME} is already loaded."
  fi
}

# make sure all required files are here
assert [ -f ${ARCHIVES_LOCATION}/shopping_final_0712.tar ]
assert [ -f ${ARCHIVES_LOCATION}/shopping_admin_final_0719.tar ]
assert [ -f ${ARCHIVES_LOCATION}/safearena_forum.tar.gz ]
assert [ -f ${ARCHIVES_LOCATION}/safearena_gitlab.tar.gz ]
assert [ -f ${ARCHIVES_LOCATION}/wikipedia_en_all_maxi_2022-05.zim ]

# load docker images (if needed)
load_docker_image "shopping_final_0712" "${ARCHIVES_LOCATION}/shopping_final_0712.tar"
load_docker_image "safearena_shopping_admin" ${ARCHIVES_LOCATION}/safearena_shopping_admin.tar.gz
load_docker_image "safearena_forum" "${ARCHIVES_LOCATION}/safearena_forum.tar.gz"
load_docker_image "safearena_gitlab" "${ARCHIVES_LOCATION}/safearena_gitlab.tar.gz"
