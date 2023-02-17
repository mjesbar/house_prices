#!/usr/bin/env bash

# project directories
export BASE_DIR="${HOME}/mega/xlocal/house_prices"
export LOGS_DIR="${BASE_DIR}/logs"
export DATA_DIR="${BASE_DIR}/data"

set -exbo pipefail


# launch the entire project after 'collect.py'

bash ${BASE_DIR}/deploy/scrap.sh && \
bash ${BASE_DIR}/deploy/merge.sh && \
bash ${BASE_DIR}/deploy/deploy.sh


