#!/bin/sh

ip=$(ip a|egrep 'inet[^6]'|fgrep -v 127.0.0.1|sed -r -e 's/.*inet ([0-9.]+).*/\1/g'|head -1)

urls="\
http://${ip}:9494/v1/reports/projects/resultset/ \
http://${ip}:9494/v1/reports/projects/resultset \
http://${ip}:9494/v1/reports/projects/ \
http://${ip}:9494/v1/reports/projects \
http://${ip}:9494/v1/reports/ \
http://${ip}:9494/v1/reports \
http://${ip}:9494/v1/ \
http://${ip}:9494/v1 \
http://${ip}:9494/ \
http://${ip}:9494 \
"

for url in $urls ; do
	echo "$url"
	curl "$url"
	ret=$?
	echo
	if [ $ret -ne 0 ] ; then
		echo "Error on URL '$url'" 1>&2
		exit $?
	fi
done

exit 0
