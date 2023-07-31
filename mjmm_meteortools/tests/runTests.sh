#!/bin/bash

[ -f ~/dev/config.ini ] && source ~/dev/config.ini
[ -f ~/source/testing/config.ini ] && source ~/source/testing/config.ini
[ -f ~/source/ukmon-pitools/live.key ] && source ~/source/ukmon-pitools/live.key

export PYTHONPATH=$WMPL_LOC:$RMS_LOC:.:..
echo running on $(hostname)

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here/..

if [  "$(which conda)" == "" ] ; then 
    source $HOME/venvs/${WMPL_ENV}/bin/activate
else
    conda activate $HOME/miniconda3/envs/${WMPL_ENV}
fi
pip install pytest pytest-cov 
pip install --upgrade ukmon_meteortools
echo $WMPL_LOC
pytest -v --cov=. --cov-report=term-missing tests/test_fileformats.py tests/test_ukmondb.py tests/test_utils.py
deactivate
[ -f ~/vRMS/bin/activate ] && source ~/vRMS/bin/activate
pushd $RMS_LOC
pip install pytest pytest-cov 
pip install --upgrade ukmon_meteortools
pytest -v --cov=. --cov-report=term-missing  tests/test_rmsutils.py
popd

if [ $# == 0 ] ; then
    pytest -v ./tests 
else
    pytest -v ./tests/test_$1.py --cov=$1 --cov-report=term-missing
fi
