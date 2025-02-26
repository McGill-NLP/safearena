# check if SUFFIX is set, otherwise throw an error
if [ -z ${SUFFIX+x} ]; then
    echo "SUFFIX is not set. Please set it in the calling script. Stopping script."
    return 1
fi

# check that DOMAIN_NAME is set, otherwise throw an error
if [ -z ${DOMAIN_NAME+x} ]; then
    echo "DOMAIN_NAME is not set. Please set it in the calling script. Stopping script."
    return 1
fi

DISABLE_PRINT=${DISABLE_PRINT:-"false"}

export WA_HOMEPAGE="https://sa-homepage-${SUFFIX}.${DOMAIN_NAME}"
export WA_SHOPPING="https://sa-shopping-${SUFFIX}.${DOMAIN_NAME}/"
export WA_SHOPPING_ADMIN="https://sa-shopping-admin-${SUFFIX}.${DOMAIN_NAME}/admin"
export WA_REDDIT="https://sa-forum-${SUFFIX}.${DOMAIN_NAME}"
export WA_GITLAB="https://sa-gitlab-${SUFFIX}.${DOMAIN_NAME}"
export WA_FULL_RESET="https://sa-reset-${SUFFIX}.${DOMAIN_NAME}"
# Those are not functional sites but are emptily defined here for compatibility with browsergym
export WA_WIKIPEDIA="https://sa-wikipedia-${SUFFIX}.${DOMAIN_NAME}/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export WA_MAP="https://sa-map-${SUFFIX}.${DOMAIN_NAME}"

export SAFEARENA_TASK="safe"

if [ "$DISABLE_PRINT" = "false" ]; then
    echo "Modified WA_HOMEPAGE to $WA_HOMEPAGE"
    echo "Modified WA_SHOPPING to $WA_SHOPPING"
    echo "Modified WA_SHOPPING_ADMIN to $WA_SHOPPING_ADMIN"
    echo "Modified WA_REDDIT to $WA_REDDIT"
    echo "Modified WA_GITLAB to $WA_GITLAB"
    echo "Modified WA_FULL_RESET to $WA_FULL_RESET"
    echo "Modified WA_WIKIPEDIA to $WA_WIKIPEDIA"
    echo "Modified WA_MAP to $WA_MAP"
    echo "Modified SAFEARENA_TASK to $SAFEARENA_TASK"
fi