#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
cd ..
mkdir -p testdata
cd testdata

SHAOUT=($(cat flowcam_polina_pontoon_0707_r1* | sha256sum -b))
SHAOUT=${SHAOUT[0]}
if [ "$SHAOUT" = "692ece92694019cf15a85a0012c1191aa0f88f86b919fbb0902317b8d350469e" ]; then
    echo "Test data OK, skipping download"
else
    echo "Test data hash ($SHAOUT) did not match expected output, redownloading data"
    rm -r flowcam_polina_pontoon_0707_r1
    wget https://repo.alexbaldwin.dev/open-data/flowcam/2025-07-07/r1.zip
    unzip r1.zip
    rm r1.zip
fi

SHAOUT=($(cat flowcam_polina_pontoon_0907_r2* | sha256sum -b))
SHAOUT=${SHAOUT[0]}
if [ "$SHAOUT" = "692ece92694019cf15a85a0012c1191aa0f88f86b919fbb0902317b8d350469e" ]; then
    echo "Test data OK, skipping download"
else
    echo "Test data hash ($SHAOUT) did not match expected output, redownloading data"
    rm -r flowcam_polina_pontoon_0907_r2
    wget https://repo.alexbaldwin.dev/open-data/flowcam/2025-07-09/r2.zip
    unzip r2.zip
    rm r2.zip
fi
