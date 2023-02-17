#!/usr/bin/env bash

# this script simply runs the scrapping process through all the websites choosen to scratch
# this must be executed before 'merge.sh' script
# for simple run execute 'activate_project.sh' script to run all the things set

# project directories
export BASE_DIR="${HOME}/mega/xlocal/house_prices"
export LOGS_DIR="${BASE_DIR}/logs"
export DATA_DIR="${BASE_DIR}/data"

echo
echo "Starting process ... "

set -exbo pipefail

# invoke the collect script, which stacks all the links to scrap
# comment the following 2 lines if desire run sacrp links only
echo "Executing 'collect.py' ... "
python3 ${BASE_DIR}/collect.py

if [[ $? -eq 0 ]]
then
    sleep 1
    # invoke the scrap process which will get all the information into the csv data
    echo "Executing scrap background process ... "
    python3 ${BASE_DIR}/mecu.py &
    python3 ${BASE_DIR}/finra.py &
    python3 ${BASE_DIR}/punpro.py &
else
    echo "ERROR $!"
fi

# wait for the three python3 background processes
wait -n $(ps | \
    grep -w "python3" | \
    tr -s ' ' | \
    cut -d ' ' -f 2) # output PID list of the python's background processes

# cleaning chrome driver instances, wheater python scripts fail quiting them
killall chrome
killall chrome-driver
echo "All the ChromeDriver instances were properly closed"

