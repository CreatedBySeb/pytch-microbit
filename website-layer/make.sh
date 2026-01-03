#!/bin/bash

if [ -z "$PYTCH_DEPLOYMENT_ID" ]; then
    echo "PYTCH_DEPLOYMENT_ID must be set"
    exit 1
fi

BUILD_DIR="$(realpath "$(dirname "$0")")"
REPO_ROOT="$(realpath "$BUILD_DIR"/..)"

cd "$REPO_ROOT"

LAYER_DIR=website-layer/layer-content
MICROBIT_DIR="$LAYER_DIR"/microbit/"$PYTCH_DEPLOYMENT_ID"

if [ -e node_modules -o -e $LAYER_DIR ]; then
    echo "Must be run in a clean clone"
    echo '(i.e., no "node_modules" or "'"$LAYER_DIR"'")'
    exit 1
fi

npm ci
npm run build

mkdir -p "$MICROBIT_DIR"

(
    cd build
    # Exclude v1 for now while it isn't working
    cp pytch-microbit-v2.hex \
       ../"$MICROBIT_DIR"
)

(
    cd "$LAYER_DIR"
    find microbit -type d -print0 | xargs -0 chmod 755
    find microbit -type f -print0 | xargs -0 chmod 644
    zip -r ../layer.zip microbit
)
