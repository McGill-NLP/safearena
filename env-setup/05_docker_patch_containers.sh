#!/bin/bash

# stop if any error occur
set -e

GITLAB_NUM_CORES=8


if [ "$HOST_WITH_CLOUDFLARE" = "true" ]; then
    source 00cf_vars.sh
else
    source 00_vars.sh
fi


# reddit - make server more responsive
echo "[[[Updating reddit]]]"
sudo docker exec $FORUM_CONTAINER_NAME sed -i \
  -e 's/^pm.max_children = .*/pm.max_children = 32/' \
  -e 's/^pm.start_servers = .*/pm.start_servers = 10/' \
  -e 's/^pm.min_spare_servers = .*/pm.min_spare_servers = 5/' \
  -e 's/^pm.max_spare_servers = .*/pm.max_spare_servers = 20/' \
  -e 's/^;pm.max_requests = .*/pm.max_requests = 500/' \
  /usr/local/etc/php-fpm.d/www.conf
sudo docker exec $FORUM_CONTAINER_NAME supervisorctl restart php-fpm

# shopping + shopping admin
echo "[[[Updating shopping]]]"
sudo docker exec $SHOPPING_CONTAINER_NAME /var/www/magento2/bin/magento setup:store-config:set --base-url=$SHOPPING_BASE_URL # no trailing /
sudo docker exec $SHOPPING_CONTAINER_NAME mysql -u magentouser -pMyPassword magentodb -e  "UPDATE core_config_data SET value='${SHOPPING_BASE_URL}/' WHERE path = 'web/secure/base_url';"
# remove the requirement to reset password
sudo docker exec $SHOPPING_ADMIN_CONTAINER_NAME php /var/www/magento2/bin/magento config:set admin/security/password_is_forced 0
sudo docker exec $SHOPPING_ADMIN_CONTAINER_NAME php /var/www/magento2/bin/magento config:set admin/security/password_lifetime 0
sudo docker exec $SHOPPING_CONTAINER_NAME /var/www/magento2/bin/magento cache:flush

sudo docker exec $SHOPPING_ADMIN_CONTAINER_NAME /var/www/magento2/bin/magento setup:store-config:set --base-url=$SHOPPING_ADMIN_BASE_URL
sudo docker exec $SHOPPING_ADMIN_CONTAINER_NAME mysql -u magentouser -pMyPassword magentodb -e  "UPDATE core_config_data SET value='${SHOPPING_ADMIN_BASE_URL}/' WHERE path = 'web/secure/base_url';"
sudo docker exec $SHOPPING_ADMIN_CONTAINER_NAME /var/www/magento2/bin/magento cache:flush

# gitlab
echo "[[[Updating gitlab]]]"
sudo docker exec $GITLAB_CONTAINER_NAME sed -i "s|^external_url.*|external_url '${GITLAB_BASE_URL}'|" /etc/gitlab/gitlab.rb
sudo docker exec $GITLAB_CONTAINER_NAME bash -c "printf '\npuma[\"worker_processes\"] = ${GITLAB_NUM_CORES}\n' >> /etc/gitlab/gitlab.rb"
sudo docker exec $GITLAB_CONTAINER_NAME gitlab-ctl reconfigure
