#!/bin/bash

# prepare container image
if ! podman images -n | grep -q opi_base ; then
	echo "Preparing container"
	podman run -td --dns=1.1.1.1 --name=opi_base opensuse/tumbleweed
	podman exec -it opi_base zypper -n ref
	# opi dependencies
	podman exec -it opi_base zypper -n install sudo python3 python3-requests python3-lxml python3-termcolor curl

	# test dependencies
	podman exec -it opi_base zypper -n install python3-pexpect

	podman commit opi_base opi_base
	podman kill opi_base
fi



opi_dir="$(dirname $(pwd)/$0)/../"
podman run -ti --volume "${opi_dir}:/opi/" opi_base /opi/test/run.sh $1
exit $?
