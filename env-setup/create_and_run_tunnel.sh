source 00_vars.sh

# create a function that delete, create, route, and run a tunnel
create_route_and_run_tunnel() {
    CF_TUNNEL_NAME=$1
    CF_TUNNEL_PORT=$2

    # delete the tunnel if it exists, and recreate it
    echo "Cleaning up tunnel: $CF_TUNNEL_NAME"
    cloudflared tunnel cleanup $CF_TUNNEL_NAME
    echo "Deleting tunnel: $CF_TUNNEL_NAME"
    cloudflared tunnel delete $CF_TUNNEL_NAME
    echo "Creating tunnel: $CF_TUNNEL_NAME"
    cloudflared tunnel create $CF_TUNNEL_NAME

    # route and start the tunnel
    echo "Routing tunnel: $CF_TUNNEL_NAME"
    cloudflared tunnel route dns --overwrite-dns $CF_TUNNEL_NAME "${CF_TUNNEL_NAME}.${CF_DOMAIN}"
    echo "Running tunnel \"$CF_TUNNEL_NAME\" at URL: https://${CF_TUNNEL_NAME}.${CF_DOMAIN}"
    cloudflared tunnel run --url http://127.0.0.1:$CF_TUNNEL_PORT $CF_TUNNEL_NAME
}

create_route_and_run_tunnel $1 $2