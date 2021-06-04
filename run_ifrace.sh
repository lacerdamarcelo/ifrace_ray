#!/bin/bash

ray start --block --head --redis-port=6379 --num-cpus="${1}" --memory=3200000000 --object-store-memory=3200000000 --redis-password="123456" &
sleep 10
python run_ifrace.py 127.0.0.1:6379 123456 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12} ${13} ${14}
