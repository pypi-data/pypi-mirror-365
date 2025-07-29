#!/bin/bash
set -ex

rm -rf ./build

# Compile wheels
for PYBIN in /opt/python/cp{37,38,39,310,311}*/bin; do
    "${PYBIN}/python" setup.py bdist_wheel -d ./tmp/dist
done

# Bundle external shared libraries into the wheels
for whl in ./tmp/dist/*cp{37,38,39,310,311}*.whl; do
    auditwheel repair "$whl" -w ./dist/
done


## Install packages and test
#for PYBIN in /opt/python/cp{37,38,39,310}*/bin; do
#    "${PYBIN}/pip" install ./dist/
#done
