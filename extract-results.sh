#!/usr/bin/env bash

#
#
#


log() {
    local LEVEL=${2:-INFO}
    echo "$(date +'%Y-%m-%d %T'): $LEVEL $1"
}

# Extracts method,reqs,fails,avg_delay,min_delay,max_delay values
# from locust log file
locust_result() {
    local LOCUST_LOG=$1
    # The table appears just after "Shutting down" is reported
    # 'Total   ' is in the last row of the table
    local TABLE=`awk '/Shutting down/{flag=1;next}/Total/{flag=0}flag' "${LOCUST_LOG}"`

    # Cut header and styling --------- rows
    local RAW_ROWS=`echo "${TABLE}" | grep " GET /"`

    # Prepare values for columns method,reqs,fails,avg_delay,min_delay,max_delay
    LOCUST_STATS=`echo "${RAW_ROWS}" \
                  | sed 's/?/ /' \
                  | awk '{ print $2 "," $4 "," $5 "," $6 "," $7 "," $8 }'`

    if echo "${LOCUST_STATS}" | grep --quiet ",,"
    then
        log "Couldn't find all locust results at ${LOCUST_LOG}" "ERROR"
        exit 1
    fi
}

# Calculates duration of locust test in seconds
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

# Extracts internal servers stats from stats log
# io_ops,io_duration,cpu_ops,cpu_duration,cpu_user,cpu_system,cpu_children_user,cpu_children_system,mem_virt,mem_res,mem_uni
server_stats() {
    local STATS_LOG=$1
    local LAST_ROW=`tail -n 1 "${STATS_LOG}"`

    SERVER_STATS=`
        echo "${LAST_ROW}" |
        awk '{ print $4 "," $5 "," $7 "," $8 "," $10 "," $11 "," $12 "," $13 "," $15 "," $16 "," $17 }'
    `
    if echo "${SERVER_STATS}" | grep --quiet ",,"
    then
        log "Couldn't find all expected stats at ${STATS_LOG}" "ERROR"
        exit 1
    fi
}


OUTPUT="./results2/summary_$(date +'%Y-%m-%d_%T').csv"


# Iterate through all result directories
for result_dir in `find ./results2 -type d`
do
    # Skip results root directory
    if [[ "${result_dir}" == './results2' ]]; then
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
    # Iterate through servers
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
        PREFIX="${SCENARIO},${CLIENTS},${server}"

        echo "${LOCUST_STATS}" \
        | awk -v prefix="${PREFIX}" -v duration="${DURATION}" -v server="${SERVER_STATS}" \
              '{ print prefix "," $1 "," duration "," server }' >> "${OUTPUT}"
    done
done

mv "${OUTPUT}" "${OUTPUT}.raw"

# Write header
echo "scenario,clients,server,\
method,reqs,fails,avg_delay,min_delay,max_delay,duration,\
io_ops,io_duration,cpu_ops,cpu_duration,\
cpu_user,cpu_system,cpu_children_user,cpu_children_system,mem_virt,mem_res,mem_uni" \
> "${OUTPUT}"

# Write sorted content
sort -t , -k 1,1 -k 2,2n -k 3,3 -k 5,5 "${OUTPUT}.raw" >> "${OUTPUT}"
rm "${OUTPUT}.raw"
