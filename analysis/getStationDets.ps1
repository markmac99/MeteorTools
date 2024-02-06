# Copyright (C) 2018-2023 Mark McIntyre 

# retrieve camera owner details from AWS
# requires privileged AWS access. 

if ($args.count -lt 1) {
    write-output "usage: getStationDets.ps1 searchpattern {refresh}"
    exit 1
}
$patt = $args[0]
python -c "from reports.CameraDetails import findLocationInfo;r=findLocationInfo('$patt');print(r);"
