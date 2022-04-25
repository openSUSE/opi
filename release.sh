#!/bin/bash -ex

version=$1
changes=$(git log $(git describe --tags --abbrev=0)..HEAD --no-merges --format="- %s")

echo "__version__ = '${version}'" > opi/version.py
osc vc -m "Version ${version}\n${changes}" opi.changes
vi opi.changes
git commit opi/version.py opi.changes -m "Version ${version}"
git tag "v${version}"
read -p "Push now? "
git push
git push --tags
gh release create "v${version}"  --generate-notes

read -p "Update RPM? "
cd ~/devel/obs/utilities/opi
sed -i -e "s/^\(Version: *\)[^ ]*$/\1${version}/" opi.spec
osc vc -m "Version ${version}\n${changes}"
osc rm opi-*.tar.gz
osc service dr
osc add opi-*.tar.gz
osc st
osc diff|bat

osc ci
osc sr
