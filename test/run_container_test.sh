#!/bin/bash

base_image="${2:-opensuse/tumbleweed}"
opi_base_image="opi_base_${base_image/\//_}"

# prepare container image
if ! podman images exists $opi_base_image ; then
	echo "Preparing container"
	podman run -td --dns=1.1.1.1 --name=opi_base ${2:-opensuse/tumbleweed}
	podman exec -it opi_base zypper -n ref
	# opi dependencies
	podman exec -it opi_base zypper -n install sudo python3 python3-requests python3-lxml python3-termcolor python3-curses curl

	# test dependencies
	podman exec -it opi_base zypper -n install python3-pexpect

	podman commit opi_base $opi_base_image
	podman kill opi_base
	podman rm opi_base
fi



opi_dir="$(dirname $(pwd)/$0)/../"
podman run -ti --rm --volume "${opi_dir}:/opi/" $opi_base_image /opi/test/run.sh $1
exit $?
