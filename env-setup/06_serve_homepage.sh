#!/bin/bash

# HOST_WITH_CLOUDFLARE is the first input

if [ "$HOST_WITH_CLOUDFLARE" = "true" ]; then
    source 00cf_vars.sh
    export CF_TUNNEL_FOR_WEBARENA="true"
else
    source 00_vars.sh
    export CF_TUNNEL_FOR_WEBARENA="false"
fi

echo "CF_TUNNEL_FOR_WEBARENA: $CF_TUNNEL_FOR_WEBARENA"

# install flask in a venv
python3 -m venv venv
source venv/bin/activate
pip install flask


cd homepage
cp templates/index.backup templates/index.html
sed -i "s|SHOPPING_URL|${SHOPPING_URL}|g" templates/index.html
sed -i "s|SHOPPING_ADMIN_URL|${SHOPPING_ADMIN_URL}|g" templates/index.html
sed -i "s|GITLAB_URL|${GITLAB_URL}|g" templates/index.html
sed -i "s|REDDIT_URL|${REDDIT_URL}|g" templates/index.html
sed -i "s|WIKIPEDIA_URL|${WIKIPEDIA_URL}|g" templates/index.html

flask run --host=0.0.0.0 --port=$HOMEPAGE_PORT
