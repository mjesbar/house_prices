#!/usr/bin/env bash

# this script performs the merge of all .dat extracted data from each web scrapped,
# defining the titles, joining the three .dat files and obtaining a unique csv data file.
# the script is invoked by 'deploy.sh' after obtain both the links and their contents.

# project directories
export BASE_DIR="${HOME}/mega/xlocal/house_prices"
export LOGS_DIR="${BASE_DIR}/logs"
export DATA_DIR="${BASE_DIR}/data"

# setting titles
echo "\nMerging .dat files ..."
echo "link_index,Code,Neighborhood,City,Offer_type,Property_type,Rooms,Baths,Parking_lots,Built_area,Private_area,Stratus,Price,Price/Area,Old\n" \
    > ${DATA_DIR}/datamerge.csv
echo "\nCsv titles OK"

# merging .dat files
echo "merging mecu.dat & finra.dat & punpro.dat into a csv file ..."

if [[ -e ${BASE_DIR}/mecu.dat && -e ${BASE_DIR}/finra.dat && -e ${BASE_DIR}/punpro.dat ]]
then
    cat ${DATA_DIR}/mecu.dat ${DATA_DIR}/finra.dat ${DATA_DIR}/punpro.dat \
        >> ${DATA_DIR}/datamerge.csv
    echo "total lines appended to datamerge.cs $(wc -l ${DATA_DIR}/datamerge.csv)"
else
    echo "FileAvailableError: '.dat' files are not ready"
fi

echo "All data merged!"
echo "[Process terminated]"

# at this point the file 'datamerge.csv' must to be available to upload toward
# wheater a remote database such as AWS RDS or a data warehouse like AWS Redshift


