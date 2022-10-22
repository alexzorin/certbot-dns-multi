#!/usr/bin/env bash
set -euo pipefail;

curl -L https://go.dev/dl/go$GO_VER.linux-$GOARCH.tar.gz | tar -zx -C /usr/local/;
export PATH=$PATH:/usr/local/go/bin;
export TMP_WHEEL_DIR=/tmp/wheels

mkdir -p $TMP_WHEEL_DIR;
for PY_VER in ${PY_VERS}; do
    echo "Building for Python $PY_VER";
    /opt/python/$PY_VER/bin/pip wheel /app --no-deps -w $TMP_WHEEL_DIR;
done

for WHEEL in $TMP_WHEEL_DIR/*.whl; do
    auditwheel repair $WHEEL -w /wheels --plat $PY_PLAT
done