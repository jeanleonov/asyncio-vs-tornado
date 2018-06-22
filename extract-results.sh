#!/usr/bin/env bash

#
#
#


log() {
    local LEVEL=${2:-INFO}
    echo "$(date +'%Y-%m-%d %T'): $LEVEL $1"
}

print_locust_summary_table() {
    local LOCUST_LOG=$1
    # The table appears just after shutting down is reported
    # 'Total   ' is in the last row of the table
    awk '/Shutting down/{flag=1;next}/Total/{flag=0}flag' "${LOCUST_LOG}"
}

locust_result() {
    local LOCUST_LOG=$1
    local TABLE=`print_locust_summary_table "${LOCUST_LOG}"`
    local NO_IO=`echo "${TABLE}" | grep "/no-io?"`
    local PARALLEL_IO=`echo "${TABLE}" | grep "/parallel-io?"`
    local SEQUENTIAL_IO=`echo "${TABLE}" | grep "/sequential-io?"`

    # Save results into global variables
    NO_IO_REQS=`echo "${NO_IO}" | awk '{ print $3 }'`
    NO_IO_FAILS=`echo "${NO_IO}" | awk '{ print $4 }'`
    NO_IO_AVG=`echo "${NO_IO}" | awk '{ print $5 }'`

    PARALLEL_IO_REQS=`echo "${PARALLEL_IO}" | awk '{ print $3 }'`
    PARALLEL_IO_FAILS=`echo "${PARALLEL_IO}" | awk '{ print $4 }'`
    PARALLEL_IO_AVG=`echo "${PARALLEL_IO}" | awk '{ print $5 }'`

    SEQUENTIAL_IO_REQS=`echo "${SEQUENTIAL_IO}" | awk '{ print $3 }'`
    SEQUENTIAL_IO_FAILS=`echo "${SEQUENTIAL_IO}" | awk '{ print $4 }'`
    SEQUENTIAL_IO_AVG=`echo "${SEQUENTIAL_IO}" | awk '{ print $5 }'`

    if [ -z "${NO_IO_REQS}" ] || \
       [ -z "${NO_IO_FAILS}" ] || \
       [ -z "${NO_IO_AVG}" ] || \
       [ -z "${PARALLEL_IO_REQS}" ] || \
       [ -z "${PARALLEL_IO_FAILS}" ] || \
       [ -z "${PARALLEL_IO_AVG}" ] || \
       [ -z "${SEQUENTIAL_IO_REQS}" ] || \
       [ -z "${SEQUENTIAL_IO_FAILS}" ] || \
       [ -z "${SEQUENTIAL_IO_AVG}" ]
    then
        log "Couldn't find all locust results at ${LOCUST_LOG}" "ERROR"
        exit 1
    fi
}

locust_duration () {
    local LOCUST_LOG=$1
    local REGEX="[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}"

    # The first datetime reported in logs
    local START_TIME=`grep -o -E "${REGEX}" "${LOCUST_LOG}" | head -n 1`
    # The latest datetime mentioned in logs
    local END_TIME=`grep -o -E "${REGEX}" "${LOCUST_LOG}" | tail -n 1`

    if [ -z "${START_TIME}" ] || [ -z "${END_TIME}" ]
    then
        log "Couldn't determine test duration at ${LOCUST_LOG}" "ERROR"
        exit 1
    fi

    # Compute test duration using python
    DURATION=`python -c "
from datetime import datetime
start = datetime.strptime('${START_TIME}', '%Y-%m-%d %H:%M:%S')
end = datetime.strptime('${END_TIME}', '%Y-%m-%d %H:%M:%S')
print((end - start).seconds)
"`
}

server_stats() {
    local STATS_LOG=$1
    local LAST_ROW=`tail -n 1 "${STATS_LOG}"`

    IO_OPS=`echo "${LAST_ROW}" | awk '{ print $4 }' | sed 's/,//'`
    IO_DURATION=`echo "${LAST_ROW}" | awk '{ print $5 }' | sed 's/,//'`
    CPU_OPS=`echo "${LAST_ROW}" | awk '{ print $7 }' | sed 's/,//'`
    CPU_DURATION=`echo "${LAST_ROW}" | awk '{ print $8 }' | sed 's/,//'`
    CPU_USER=`echo "${LAST_ROW}" | awk '{ print $10 }' | sed 's/,//'`
    CPU_SYSTEM=`echo "${LAST_ROW}" | awk '{ print $11 }' | sed 's/,//'`

    if [ -z "${IO_OPS}" ] || \
       [ -z "${IO_DURATION}" ] || \
       [ -z "${CPU_OPS}" ] || \
       [ -z "${CPU_DURATION}" ] || \
       [ -z "${CPU_USER}" ] || \
       [ -z "${CPU_SYSTEM}" ]
    then
        log "Couldn't find all expected stats at ${STATS_LOG}" "ERROR"
        exit 1
    fi
}


OUTPUT="./results/summary $(date +'%Y-%m-%d %T').csv"


# Iterate through all result directories
for result_dir in `find ./results -type d`
do
    # Skip results root directory
    if [[ "${result_dir}" == './results' ]]; then
        continue;
    fi

    # Extract scenario name and number of clients from directory name
    DIR_NAME="$(basename -- "${result_dir}")"
    SCENARIO="${DIR_NAME%_*}"
    CLIENTS=`echo "${DIR_NAME##*_}" | sed 's/c//'`

    SERVERS="
asyncio
tornado2
tornado3
"
    for server in ${SERVERS}
    do
        log "Directory ${DIR_NAME}. Extracting results for ${server} server"
        # Functions below save its results to global vars

        # Fetch basic requests stats
        locust_result "${result_dir}/${server}-locust.log"

        # Determine test duration in seconds
        locust_duration "${result_dir}/${server}-locust.log"

        # Extract servers stats
        server_stats "${result_dir}/${server}-stats.log"

        # Save stats for no/parallel/sequential-io into separate rows
        PREFIX="${SCENARIO},${CLIENTS},${server},${DURATION}"
        SUFFIX="${IO_OPS},${IO_DURATION},${CPU_OPS},${CPU_DURATION},${CPU_USER},${CPU_SYSTEM}"

        echo "${PREFIX},no-io,${NO_IO_REQS},${NO_IO_FAILS},${NO_IO_AVG},${SUFFIX}" >> "${OUTPUT}"
        echo "${PREFIX},parallel-io,${PARALLEL_IO_REQS},${PARALLEL_IO_FAILS},${PARALLEL_IO_AVG},${SUFFIX}" >> "${OUTPUT}"
        echo "${PREFIX},sequential-io,${SEQUENTIAL_IO_REQS},${SEQUENTIAL_IO_FAILS},${SEQUENTIAL_IO_AVG},${SUFFIX}" >> "${OUTPUT}"
    done
done

mv "${OUTPUT}" "${OUTPUT}.raw"

# Write header
echo "scenario,clients,server,duration,method,reqs,fails,avg_delay,io_ops,io_duration,cpu_ops,cpu_duration,cpu_user,cpu_system" > "${OUTPUT}"

# Write sorted content
sort -t , -k 1,1 -k 2,2n -k 3,3 -k 5,5 "${OUTPUT}.raw" >> "${OUTPUT}"
rm "${OUTPUT}.raw"
