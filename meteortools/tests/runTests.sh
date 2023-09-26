#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here/..
echo running on $(hostname) 
pwd

if [ "$(hostname)" == "MARKSDT" ] ; then 
    . "/home/mark/miniconda3/etc/profile.d/conda.sh"
    if [ ! -f /home/mark/miniconda3/envs/mttest/bin/python ] ; then
        conda create -n mttest python=3.8 -y
    fi 
    conda activate mttest
    pip install pytest pytest-cov 
    #pip install --upgrade -r ../requirements.txt
    export PYTHONPATH=/mnt/e/dev/meteorhunting/WesternMeteorPyLib:/mnt/e/dev/meteorhuunting/RMS:.:..
else
    [ -f ~/dev/config.ini ] && source ~/dev/config.ini
    [ -f ~/source/testing/config.ini ] && source ~/source/testing/config.ini
    [ -f ~/source/ukmon-pitools/live.key ] && source ~/source/ukmon-pitools/live.key
    export PYTHONPATH=$WMPL_LOC:$RMS_LOC:.:..
    if [  "$(which conda)" == "" ] ; then 
        source $HOME/venvs/wmpl/bin/activate
    else
        conda activate $HOME/miniconda3/envs/wmpl
    fi
    pip install pytest pytest-cov 
    pip install --upgrade meteortools
fi
pytest -v --cov=. --cov-report=term-missing $here/test_fileformats.py $here/test_ukmondb.py $here/test_utils.py

if [ "$(hostname)" == "MARKSDT" ] ; then 
    conda deactivate
    conda activate RMS
    pushd /mnt/e/dev/meteorhunting/RMS
else 
    [ -f ~/vRMS/bin/activate ] && source ~/vRMS/bin/activate
    pushd $RMS_LOC
fi 
pytest -v --cov=$here/.. --cov-report=term-missing  $here/test_rmsutils.py
popd