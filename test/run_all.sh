#!/bin/bash

test_dir="$(dirname "$(pwd)/$0")"
cd "$test_dir"


failed_tests=0
total_tests=0

for t in *.py ; do
	let total_tests++
	if ! sudo ./run_container_test.sh "$t" ; then
		let failed_tests++
	fi
done

if [[ "$failed_tests" != "0" ]] ; then
	echo "$(tput bold)$(tput setaf 1)Error: ${failed_tests} out of ${total_tests} failed!$(tput sgr0)"
	exit 1
else
	echo "$(tput bold)$(tput setaf 2)All ${total_tests} tests succedeed!$(tput sgr0)"
fi
