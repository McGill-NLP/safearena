#!/bin/bash

export HOST_WITH_CLOUDFLARE=${HOST_WITH_CLOUDFLARE:-"false"}

CF_DOMAIN= "<your-cf-domain.com>"
ARCHIVES_LOCATION="</path/to/containers>"

USER_INITIAL="aa"
USER_NUM=20
INSTANCE_NUM=${CUSTOM_INSTANCE_NUM:-0}
PROJECT_NUM=0

# check that CF_DOMAIN and archives location are set
if [ "$CF_DOMAIN" = "<your-cf-domain.com>" ]; then
    echo "Please set the CF_DOMAIN variable in 00_vars.sh"
    return 1
fi

if [ "$ARCHIVES_LOCATION" = "</path/to/containers>" ]; then
    echo "Please set the ARCHIVES_LOCATION variable in 00_vars.sh"
    return 1
fi

# Port: uupia
# uu: two-digit user number, e.g. 20 -> johndoe (jd), 21 -> mary smith (ms), ...
# p: project number, e.g. 0 -> safearena, 1 -> visualwebarena
# i: instance number, e.g. 0 -> instance for experiment #1, 1 -> instance for experiment #2, ...
# a: application number, e.g. 0 -> homepage, 1 -> shopping, 2 -> reddit, ...

PUBLIC_HOSTNAME="127.0.0.1"

HOMEPAGE_PORT="${USER_NUM}${PROJECT_NUM}${INSTANCE_NUM}0"
SHOPPING_PORT="${USER_NUM}${PROJECT_NUM}${INSTANCE_NUM}1"
SHOPPING_ADMIN_PORT="${USER_NUM}${PROJECT_NUM}${INSTANCE_NUM}2"
REDDIT_PORT="${USER_NUM}${PROJECT_NUM}${INSTANCE_NUM}3"
GITLAB_PORT="${USER_NUM}${PROJECT_NUM}${INSTANCE_NUM}4"
WIKIPEDIA_PORT="${USER_NUM}${PROJECT_NUM}${INSTANCE_NUM}5"
RESET_PORT="${USER_NUM}${PROJECT_NUM}${INSTANCE_NUM}9"

SHOPPING_CONTAINER_NAME="sa_shopping_${USER_INITIAL}_${INSTANCE_NUM}"
SHOPPING_ADMIN_CONTAINER_NAME="sa_shopping_admin_${USER_INITIAL}_${INSTANCE_NUM}"
FORUM_CONTAINER_NAME="sa_forum_${USER_INITIAL}_${INSTANCE_NUM}"
GITLAB_CONTAINER_NAME="sa_gitlab_${USER_INITIAL}_${INSTANCE_NUM}"
WIKIPEDIA_CONTAINER_NAME="sa_wikipedia_${USER_INITIAL}_${INSTANCE_NUM}"
HOMEPAGE_CONTAINER_NAME="sa_homepage_${USER_INITIAL}_${INSTANCE_NUM}"
RESET_CONTAINER_NAME="sa_reset_${USER_INITIAL}_${INSTANCE_NUM}"


SHOPPING_URL="http://${PUBLIC_HOSTNAME}:${SHOPPING_PORT}"
SHOPPING_ADMIN_URL="http://${PUBLIC_HOSTNAME}:${SHOPPING_ADMIN_PORT}/admin"
REDDIT_URL="http://${PUBLIC_HOSTNAME}:${REDDIT_PORT}/forums/all"
GITLAB_URL="http://${PUBLIC_HOSTNAME}:${GITLAB_PORT}/explore"
WIKIPEDIA_URL="http://${PUBLIC_HOSTNAME}:${WIKIPEDIA_PORT}/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"

# base url, used during patching:
SHOPPING_BASE_URL="http://$PUBLIC_HOSTNAME:$SHOPPING_PORT"
SHOPPING_ADMIN_BASE_URL="http://$PUBLIC_HOSTNAME:$SHOPPING_ADMIN_PORT"
GITLAB_BASE_URL="http://$PUBLIC_HOSTNAME:$GITLAB_PORT"

# CF shorthand for the container names
HOMEPAGE_CF_NAME=${HOMEPAGE_CONTAINER_NAME//_/-}
SHOPPING_CF_NAME=${SHOPPING_CONTAINER_NAME//_/-}
SHOPPING_ADMIN_CF_NAME=${SHOPPING_ADMIN_CONTAINER_NAME//_/-}
FORUM_CF_NAME=${FORUM_CONTAINER_NAME//_/-}
GITLAB_CF_NAME=${GITLAB_CONTAINER_NAME//_/-}
WIKIPEDIA_CF_NAME=${WIKIPEDIA_CONTAINER_NAME//_/-}
RESET_CF_NAME=${RESET_CONTAINER_NAME//_/-}

# CF VERSIONS OF THE URLS
CF_HOME_URL="https://${HOMEPAGE_CF_NAME}.${CF_DOMAIN}"
CF_SHOPPING_URL="https://${SHOPPING_CF_NAME}.${CF_DOMAIN}"
CF_SHOPPING_ADMIN_URL="https://${SHOPPING_ADMIN_CF_NAME}.${CF_DOMAIN}/admin"
CF_REDDIT_URL="https://${FORUM_CF_NAME}.${CF_DOMAIN}/forums/all"
CF_GITLAB_URL="https://${GITLAB_CF_NAME}.${CF_DOMAIN}/explore"
CF_WIKIPEDIA_URL="https://${WIKIPEDIA_CF_NAME}.${CF_DOMAIN}/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"

# base url, used during patching:
CF_SHOPPING_BASE_URL="https://${SHOPPING_CF_NAME}.${CF_DOMAIN}"
CF_SHOPPING_ADMIN_BASE_URL="https://${SHOPPING_ADMIN_CF_NAME}.${CF_DOMAIN}"

# gitlab note: this url is assigned to the `external_url` in the gitlab.rb file during patching
# this external_url is used to generate the gitlab url in the cloning inside the UI. However,
# it is critical that the port used in the external_url is the same as the port used in the
# CF_GITLAB_URL. This is because the gitlab container is exposed on the same port as the CF_GITLAB_URL
# WE are also using HTTP not HTTPS because the gitlab container is not configured to use HTTPS, as it
# will try to use the letsencrypt certificates, which are not valid for the CF domain.
# In this case, we use the 443 port since it is the default HTTPS port, so when cloning, this will map
# the gitlab url to the CF domain without the need to change the port, while working with the gitlab
# container on the server side, as the gitlab container is exposed on the 443 port.
CF_GITLAB_EXTERNAL_URL="http://${GITLAB_CF_NAME}.${CF_DOMAIN}:443"

echo "Cloudflare tunneling: $HOST_WITH_CLOUDFLARE"