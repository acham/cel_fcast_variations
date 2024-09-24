#!/bin/bash

docker run \
    -v ./.env:/code/app/.env \
    -v ./data/cel.db:/data/cel.db \
    -p 8000:8000 fcast_variations
