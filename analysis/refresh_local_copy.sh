#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre 

locf=/mnt/f/videos/MeteorCam/ukmondata
if [ $# -gt 1 ] ; then
    locf=$1
fi 
pushd $locf
pwd
rsync -avz ukmonhelper2:prod/data/*.png .
rsync -avz ukmonhelper2:prod/data/*.jpg .
rsync -avz ukmonhelper2:prod/data/single/*.csv single/
rsync -avz ukmonhelper2:prod/data/single/*.snap single/
rsync -avz ukmonhelper2:prod/data/matched/*.csv matched/
rsync -avz ukmonhelper2:prod/data/matched/*.snap matched/
rsync -avz ukmonhelper2:prod/data/consolidated/ consolidated/
rsync -avz ukmonhelper2:prod/data/latest/ latest/
rsync -avz ukmonhelper2:prod/data/dailyreports/ dailyreports/
rsync -avz ukmonhelper2:prod/data/searchidx/ searchidx/
rsync -avz ukmonhelper2:prod/data/admin/ admin/
rsync -avz ukmonhelper2:prod/data/browse/ browse/
rsync -avz ukmonhelper2:prod/logs/*.log logs/ 
find logs/ -mtime +30 -exec rm -f {} \;
popd