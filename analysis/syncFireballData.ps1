$here=get-location
set-location f:\videos\meteorcam\fireballs
aws s3 sync 2024 s3://ukmon-shared/fireballs/2024/ --exclude "*" --include "2024*" --exclude "*.bz2" --exclude "*nogood*" --profile ukmon-markmcintyre
aws s3 sync 2023 s3://ukmon-shared/fireballs/2023/ --exclude "*" --include "2023*"  --exclude "*.bz2" --exclude "*nogood*"  --profile ukmon-markmcintyre
aws s3 sync nonukmon s3://ukmon-shared/fireballs/nonukmon/ --exclude "*" --include "nonukmon" --exclude "*.bz2" --exclude "*nogood*" --profile ukmon-markmcintyre

aws s3 sync 2024 s3://ukmda-shared/fireballs/2024/ --exclude "*" --include "2024*" --exclude "*.bz2" --exclude "*nogood*" --profile ukmda_admin
aws s3 sync 2023 s3://ukmda-shared/fireballs/2023/ --exclude "*" --include "2023*"  --exclude "*.bz2" --exclude "*nogood*"  --profile ukmda_admin
aws s3 sync nonukmon s3://ukmda-shared/fireballs/nonukmon/ --exclude "*" --include "nonukmon" --exclude "*.bz2" --exclude "*nogood*" --profile ukmda_admin

set-location ../sprites
aws s3 sync sprites s3://ukmda-shared/sprites/ --exclude "*" --exclude "*.bz2" --exclude "*nogood*" --profile ukmda_admin
set-location $here