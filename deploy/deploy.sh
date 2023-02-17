#!/usr/bin/env bash

# project directories
export BASE_DIR="${HOME}/mega/xlocal/house_prices"
export LOGS_DIR="${BASE_DIR}/logs"
export DATA_DIR="${BASE_DIR}/data"

# mysq credentials variables
declare password=$(cat ${BASE_DIR}/deploy/db_credentials.json | jq '.password' -r )
declare username=$(cat ${BASE_DIR}/deploy/db_credentials.json | jq '.username' -r )
declare host=$(cat ${BASE_DIR}/deploy/db_credentials.json | jq '.host' -r )
declare port=$(cat ${BASE_DIR}/deploy/db_credentials.json | jq '.port' -r )

set -exbo pipefail

dbinstances=( $(aws rds describe-db-instances | jq '.DBInstances[].DBInstanceIdentifier' -r) )
dbidentifier='houseprices'
matchdb=$(echo ${dbinstances[@]} | grep -w "${dbidentifier}")

# create the db instance
if [ -e "${BASE_DIR}/deploy/db_credentials.json" ] && [ -z ${matchdb} ]
then
    aws rds create-db-instance \
        --cli-input-json "file://${BASE_DIR}/deploy/db_instance_cli_input.json" \
        1> /dev/null
fi

# authorize IP connection to RDS database endpoint host, vi TCP port 3306
if [[ -e "${BASE_DIR}/deploy/vpc_egress_auth.json" && -e "${BASE_DIR}/deploy/vpc_ingress_auth.json" ]]
then
    aws ec2 authorize-security-group-ingress \
        --cli-input-json "file://${BASE_DIR}/deploy/vpc_ingress_auth.json" \
        1> /dev/null
    aws ec2 authorize-security-group-egress \
        --cli-input-json "file://${BASE_DIR}/deploy/vpc_egress_auth.json" \
        1> /dev/null
else
    echo "FileSetUpError: either egress or ingress json authorize configuration files"
    echo "are not present in your current project -path '${BASE_DIR}'"
fi

# load 'datamerge.csv' into rds remote database
mysql \
    --host=${host} \
    --port=${port} \
    --user=${username} \
    --password=${password} \
    --local-infile \
    < "${BASE_DIR}/deploy/db_setup.sql"

if [[ $? -eq 0 ]]
then echo -e "\nData loaded! dataset now available in rds db instance to make analysis"
else echo "DeployInstanceError: something went wrong dude"
fi

