#!/bin/bash

echo "$(tput bold)$(tput setaf 6)===== Running test: $1 =====$(tput sgr0)"

cd /opi/
./test/$1
result=$?

if [[ "$result" == "0" ]] ; then
	echo "$(tput bold)$(tput setaf 2)>>>>> PASSED <<<<<$(tput sgr0)"
else
	echo "$(tput bold)$(tput setaf 1)!!!!! FAILED !!!!!$(tput sgr0)"
fi

exit $result
