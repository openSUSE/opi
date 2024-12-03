#!/bin/bash -x

base_image="${2:-opensuse/tumbleweed}"
opi_base_image="opi_base_${base_image/\//_}"

if [[ "$2" == "opensuse/microos" ]] ; then
	base_image="opensuse/tumbleweed"
	opi_base_image="opi_base_opensuse_microos"
fi

# prepare container image
if ! podman image exists $opi_base_image ; then
	echo "Preparing container"
	podman run -td --dns=1.1.1.1 --name=opi_base $base_image
	podman exec -it opi_base zypper -n ref

	if [[ "$2" == "opensuse/microos" ]] ; then
		# fake MicroOS
		podman exec -it opi_base zypper -n install --force-resolution MicroOS-release
	fi

	# opi dependencies
	podman exec -it opi_base zypper -n install sudo python3 python3-requests python3-lxml python3-termcolor python3-curses python3-rpm curl rpm-build squashfs python3-pip python3-setuptools

	# test dependencies
	podman exec -it opi_base zypper -n install python3-pexpect shadow

	podman commit opi_base $opi_base_image
	podman kill opi_base
	podman rm opi_base
fi



opi_dir="$(dirname $(pwd)/$0)/../"
test_module=$(basename $1)
podman run -ti --rm --volume "${opi_dir}:/opi/" $opi_base_image /opi/test/run.sh $test_module
exit $?
