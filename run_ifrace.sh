#!/bin/bash

ray start --block --head --redis-port=6380 --num-cpus=4 --memory=400000000 --object-store-memory=200000000 --redis-password="123456" &
sleep 10
python run_ifrace.py 127.0.0.1:6379 123456 hclpso_config.json HCLPSO CEC17 cec17_config/cec17_ifrace_func1_instances.txt 8 10 0.3 1 5 15 15 300 hclpso_test.txt