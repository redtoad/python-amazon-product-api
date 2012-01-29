# Watches source directory for file changes and rebuilds entire docu
# Sebastian Rahlf -- 2012-01-30 00:31:16

SOURCE=`pwd`/source
IGNORE="--exclude \..*\.sw\w?" # ignore vim swap files
OPTIONS="-r -e modify -e create -e delete"

while inotifywait $OPTIONS $IGNORE $SOURCE
do 
    make clean && make html
done
