#!/bin/bash

docker run \
  --env-file conf.env \
  --rm \
  --name "studentiunimi_user_$1" \
  --mount "type=bind,src=$(pwd)/sessions/$1.session,dst=/usr/src/app/telegram.session" \
  ghcr.io/studentiunimi/userbot-worker
