source vars/safe-cf.sh

# for harmful tasks, we use the admin version of the shopping site, which has a storefront
# with harmful products not present in the regular shopping site
export WA_SHOPPING="https://sa-shopping-admin-${SUFFIX}.${DOMAIN_NAME}"
export SAFEARENA_TASK="harm"

if [ "$DISABLE_PRINT" = "false" ]; then
    echo "Modified WA_SHOPPING to $WA_SHOPPING"
    echo "Modified SAFEARENA_TASK to $SAFEARENA_TASK"
fi