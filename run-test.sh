#!/bin/bash

#
#
#

set -e
set -u


# Defaults values for arguments.
SCENARIO="./test-scenarios/norm-io-ops low-io-delay low-cpu.yml"
REQUESTS=200
CLIENTS=40
HATCH_RATE=5

BACKEND_PORT=8080
ASYNCIO_PORT=8081
TORNADO2_PORT=8082
TORNADO3_PORT=8083

# Save arguments to add it into results
ARGUMENTS=$@

usage() {
    echo "Usage: ${0} [--scenario <file>][--requests <int>][--clients <int>][--hatch_rate <int>]"
    echo
    echo "Options:"
    echo "   --scenario <file>   Scenario file to use (default $SCENARIO)"
    echo "   --requests <int>    Number of requests locusts should send (default $REQUESTS)"
    echo "   --clients <int>     Number of clients to simulate (default $CLIENTS)"
    echo "   --hatch-rate <int>  Rate per second in which clients are spawned (default $HATCH_RATE)"
    exit 1
}

# Let's get the  command line arguments.
while [ $# -gt 0 ]; do
    if [ "${1}" = "--scenario" ]; then
        shift
        if [ -z "${1}" ]; then
            usage
        fi
        SCENARIO="${1}"
        shift
        continue
    fi
    if [ "${1}" = "--requests" ]; then
        shift
        if [ -z "${1}" ]; then
            usage
        fi
        REQUESTS="${1}"
        shift
        continue
    fi
    if [ "${1}" = "--clients" ]; then
        shift
        if [ -z "${1}" ]; then
            usage
        fi
        CLIENTS="${1}"
        shift
        continue
    fi
    if [ "${1}" = "--hatch-rate" ]; then
        shift
        if [ -z "${1}" ]; then
            usage
        fi
        HATCH_RATE="${1}"
        shift
        continue
    fi
    usage
done


log() {
    LEVEL=${2:-INFO}
    echo "$(date +'%Y-%m-%d %T'): $LEVEL $1"
}

ensure_server() {
    # Rename arguments
    SERVER_NAME="$1"
    SERVER_PORT="$2"

    # Give server a second to start
    sleep 1

    # Try to find expected server PID
    SERVER_PID=`jobs -l | grep "${SERVER_NAME}" | awk '{ print $2 }'`
    # Find actual server listening on specified port
    LISTENER_PID=`netstat -nlp 2>/dev/null | grep ":${SERVER_PORT} " |
                  awk '{ print $7 }' | awk -F '/' '{ print $1 }' | head -1`

    if [ "${SERVER_PID}" != "${LISTENER_PID}" ]; then
         log "$1 server is not listening on ${SERVER_PORT}" "ERROR"
         log "Logs can be found at '${RESULTS}'"
         exit 1
    fi
}

kill_jobs() {
    jobs -p | xargs kill
}
trap kill_jobs EXIT


RESULTS="results/$(date +'%Y-%m-%d %T')"
mkdir -p "${RESULTS}"

# Export scenario for locust
export SCENARIO

# Save test inputs into results directory
cp "${SCENARIO}" "${RESULTS}/scenario.yml"
echo "${ARGUMENTS}" > "${RESULTS}/arguments"

VENV2=test-venv2
VENV3=test-venv3

if [ ! -f "${VENV2}/bin/python" ]; then
    log "Creating Python2 virtual environment"
    virtualenv ${VENV2} --python=python2
fi
log "Ensuring that dependencies are installed for python2"
${VENV2}/bin/pip2 install --quiet -r requirements-python2.txt

if [ ! -f "${VENV3}/bin/python" ]; then
    log "Creating Python3 virtual environment"
    virtualenv ${VENV3} --python=python3
fi
log "Ensuring that dependencies are installed for python3"
${VENV3}/bin/pip3 install --quiet -r requirements-python3.txt


log "Starting dummy backend server on port ${BACKEND_PORT}"
${VENV3}/bin/python3 ./backend.py \
                     --port ${BACKEND_PORT} \
                     > "${RESULTS}/backend.log" 2>&1 &

ensure_server "backend.py" ${BACKEND_PORT}


log ""
log "===================================="
log "Starting asyncio server on port ${ASYNCIO_PORT}"
${VENV3}/bin/python3 ./asyncio_server.py \
                     --port ${ASYNCIO_PORT} \
                     --stats-output "${RESULTS}/asyncio-stats.log" \
                     > "${RESULTS}/asyncio.log" 2>&1 &

ensure_server "asyncio_server.py" ${ASYNCIO_PORT}

log "Running load test using locustio"
test-venv3/bin/locust \
    --no-web \
    --host="http://localhost:${ASYNCIO_PORT}" \
    --num-request=${REQUESTS} \
    --clients=${CLIENTS} \
    --hatch-rate=${HATCH_RATE} \
    --only-summary \
    --no-reset-stats \
    2>&1 | tee "${RESULTS}/asyncio-locust.log"

log "Terminating asyncio server"
jobs -l | grep "asyncio_server.py" | awk '{ print $2 }' | xargs kill


log ""
log "=============================================="
log "Starting tornado (Python2) server on port ${TORNADO2_PORT}"
${VENV2}/bin/python2 ./tornado_server.py \
                    --port ${TORNADO2_PORT} \
                    --stats-output "${RESULTS}/tornado2-stats.log" \
                    > "${RESULTS}/tornado2.log" 2>&1 &

ensure_server "tornado_server.py" ${TORNADO2_PORT}

log "Running load test using locustio"
test-venv3/bin/locust \
    --no-web \
    --host="http://localhost:${TORNADO2_PORT}" \
    --num-request=${REQUESTS} \
    --clients=${CLIENTS} \
    --hatch-rate=${HATCH_RATE} \
    --only-summary \
    --no-reset-stats \
    2>&1 | tee "${RESULTS}/tornado2-locust.log"

log "Terminating tornado server"
jobs -l | grep "tornado_server.py" | awk '{ print $2 }' | xargs kill


log ""
log "=============================================="
log "Starting tornado (Python3) server on port ${TORNADO3_PORT}"
${VENV3}/bin/python3 ./tornado_server.py \
                     --port ${TORNADO3_PORT} \
                     --stats-output "${RESULTS}/tornado3-stats.log" \
                     > "${RESULTS}/tornado3.log" 2>&1 &

ensure_server "tornado_server.py" ${TORNADO3_PORT}

log "Running load test using locustio"
test-venv3/bin/locust \
    --no-web \
    --host="http://localhost:${TORNADO3_PORT}" \
    --num-request=${REQUESTS} \
    --clients=${CLIENTS} \
    --hatch-rate=${HATCH_RATE} \
    --only-summary \
    --no-reset-stats \
    2>&1 | tee "${RESULTS}/tornado3-locust.log"

log "Terminating tornado server"
jobs -l | grep "tornado_server.py" | awk '{ print $2 }' | xargs kill


log ""
log "Now you can find results at ${RESULTS}"
exit 0
