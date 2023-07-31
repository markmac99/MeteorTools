#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre 

locf=/mnt/f/videos/MeteorCam/ukmondata
if [ $# -gt 1 ] ; then
    locf=$1
fi 
pushd $locf
pwd
rsync -avz ukmonhelper:ukmon-shared/kmls/* kmls/
rsync -avz ukmonhelper:prod/data/*.png .
rsync -avz ukmonhelper:prod/data/*.jpg .
rsync -avz ukmonhelper:prod/data/single/*.csv single/
rsync -avz ukmonhelper:prod/data/single/*.snap single/
rsync -avz ukmonhelper:prod/data/matched/*.csv matched/
rsync -avz ukmonhelper:prod/data/matched/*.snap matched/
rsync -avz ukmonhelper:prod/data/consolidated/ consolidated/
rsync -avz ukmonhelper:prod/data/latest/ latest/
rsync -avz ukmonhelper:prod/data/dailyreports/ dailyreports/
rsync -avz ukmonhelper:prod/data/searchidx/ searchidx/
rsync -avz ukmonhelper:prod/data/admin/ admin/
rsync -avz ukmonhelper:prod/data/browse/ browse/
rsync -avz ukmonhelper:prod/logs/ logs/ 
find logs/ -mtime +30 -exec rm -f {} \;
popd