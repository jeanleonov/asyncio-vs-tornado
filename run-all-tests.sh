#!/usr/bin/env bash

#
#
#

./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 7 --requests 2000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 7 --requests 12000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/hightraffic.yml'              --clients 7 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 7 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 7 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 7 --requests 6000 --hatch-rate 5

#./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 15 --requests 2000 --hatch-rate 5
#./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 15 --requests 12000 --hatch-rate 5
#./run-test.sh --scenario 'test-scenarios/hightraffic.yml'              --clients 15 --requests 6000 --hatch-rate 5
#./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 15 --requests 6000 --hatch-rate 5
#./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 15 --requests 6000 --hatch-rate 5
#./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 15 --requests 6000 --hatch-rate 5

./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 30 --requests 2000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 30 --requests 12000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/hightraffic.yml'              --clients 30 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 30 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 30 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 30 --requests 6000 --hatch-rate 5

./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 60 --requests 2000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 60 --requests 12000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/hightraffic.yml'              --clients 60 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 60 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 60 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 60 --requests 6000 --hatch-rate 5

./run-test.sh --scenario 'test-scenarios/highdelay_lowcpu.yml'         --clients 120 --requests 2000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/highops_lowdelay_tinycpu.yml' --clients 120 --requests 12000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/hightraffic.yml'              --clients 120 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/hugetraffic.yml'              --clients 120 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/lowdelay_highcpu.yml'         --clients 120 --requests 6000 --hatch-rate 5
./run-test.sh --scenario 'test-scenarios/normal.yml'                   --clients 120 --requests 6000 --hatch-rate 5

