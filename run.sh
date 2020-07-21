#!/bin/bash
#  --scale firefox=5

for i in {1..10}
do
  bash -c "SUBNET=$i docker-compose -f proxy-stack-hub.yaml -p test$i up --abort-on-container-exit --exit-code-from controller --build --force-recreate" &
  sleep 20
done

