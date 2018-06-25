#!/usr/bin/env bash

#
#
#

./run-test.sh --scenario 'test-scenarios/highcpu.yml'                  --clients 10 --requests 2000 --hatch-rate 5 --results results2

exit 0

./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 10 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highdelay.yml'                --clients 10 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 10 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 10 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 10 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 10 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinycpu.yml'                  --clients 10 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinydelay.yml'                --clients 10 --requests 4000 --hatch-rate 5 --results results2

./run-test.sh --scenario 'test-scenarios/highcpu.yml'                  --clients 20 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 20 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highdelay.yml'                --clients 20 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 20 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 20 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 20 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 20 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinycpu.yml'                  --clients 20 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinydelay.yml'                --clients 20 --requests 4000 --hatch-rate 5 --results results2

./run-test.sh --scenario 'test-scenarios/highcpu.yml'                  --clients 40 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 40 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highdelay.yml'                --clients 40 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 40 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 40 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 40 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 40 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinycpu.yml'                  --clients 40 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinydelay.yml'                --clients 40 --requests 4000 --hatch-rate 5 --results results2

./run-test.sh --scenario 'test-scenarios/highcpu.yml'                  --clients 80 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 80 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highdelay.yml'                --clients 80 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 80 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 80 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 80 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 80 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinycpu.yml'                  --clients 80 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinydelay.yml'                --clients 80 --requests 4000 --hatch-rate 5 --results results2

./run-test.sh --scenario 'test-scenarios/highcpu.yml'                  --clients 160 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 160 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highdelay.yml'                --clients 160 --requests 2000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 160 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 160 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 160 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 160 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinycpu.yml'                  --clients 160 --requests 4000 --hatch-rate 5 --results results2
./run-test.sh --scenario 'test-scenarios/tinydelay.yml'                --clients 160 --requests 4000 --hatch-rate 5 --results results2
