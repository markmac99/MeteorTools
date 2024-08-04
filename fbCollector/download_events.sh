#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

dt=$1
basedir=$(grep basedir $here/config.ini | awk -F= '{print $2}'|tr -d '\r' | sed 's|f:|/mnt/f|g')
echo $basedir 
sleep 30
dtns=$dt 
mkdir -p $basedir/$dtns
cd $basedir/$dtns

rsync -avz gmn.uwo.ca:/home/uk*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
rsync -avz gmn.uwo.ca:/home/be*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
rsync -avz gmn.uwo.ca:/home/ie*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
rsync -avz gmn.uwo.ca:/home/nl*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
if [ "$2" == "all" ] ; then 
    rsync -avz gmn.uwo.ca:/home/fr*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
    rsync -avz gmn.uwo.ca:/home/de*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
    rsync -avz gmn.uwo.ca:/home/es*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
    rsync -avz gmn.uwo.ca:/home/ch*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
    rsync -avz gmn.uwo.ca:/home/it*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
    rsync -avz gmn.uwo.ca:/home/cz*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
    rsync -avz gmn.uwo.ca:/home/hr*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
    rsync -avz gmn.uwo.ca:/home/sk*/files/event_monitor/*${dt}*.bz2 $basedir/$dtns
fi

for f in *.bz2 ; do tar -xvf $f  ; done
if [ -d UKMON ] ; then
    sites=$(ls -1 UKMON)
    for site in $sites ; do
        cams=$(ls -1 UKMON/$site)
        for cam in $cams ; do 
            if [ -d ./$cam ] ; then rm -Rf $cam ; fi
            mv -f UKMON/$site/$cam .
        done
    done
    rm -Rf UKMON
fi 
if [ -d NEMETODE ] ; then
    sites=$(ls -1 NEMETODE)
    for site in $sites ; do
        cams=$(ls -1 NEMETODE/$site)
        for cam in $cams ; do 
            if [ -d ./$cam ] ; then rm -Rf $cam ; fi
            mv -f NEMETODE/$site/$cam .
        done
    done
    rm -Rf NEMETODE
fi 
if [ -d "UKMON,NEMETODE" ] ; then
    sites=$(ls -1 "UKMON,NEMETODE")
    for site in $sites ; do
        cams=$(ls -1 "UKMON,NEMETODE/$site")
        for cam in $cams ; do 
            if [ -d ./$cam ] ; then rm -Rf $cam ; fi
            mv -f "UKMON,NEMETODE/$site/$cam" .
        done
    done
    rm -Rf "UKMON,NEMETODE"
fi 
mkdir -p ./stacks
mkdir -p ./jpgs
mkdir -p ./mp4s
cp -f */*.jpg ./jpgs
mv -f ./jpgs/*captured_stack* ./stacks
cp -f */*.mp4 ./mp4s
