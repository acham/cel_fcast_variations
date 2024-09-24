#!/bin/bash

docker run \
    -v ./.env:/code/app/.env \
    -v ./data:/data \
    -p 8000:8000 fcast_variations
