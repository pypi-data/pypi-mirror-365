#!/bin/bash
set -ex

for PYBIN in /opt/python/cp{37,38,39,310,311}*/bin; do
    "${PYBIN}/pip" install -U setuptools setuptools-rust wheel
done
