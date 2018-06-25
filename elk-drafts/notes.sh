# See https://elk-docker.readthedocs.io/#usage for more info on elk docker image

#------------------------
# On the host machine:

# Before starting container:
sudo sysctl -w vm.max_map_count=262144

# Download image
sudo docker pull sebp/elk

# Start container for the first time
sudo docker run -p 5601:5601 -p 9200:9200 -p 5044:5044 -it --name elk sebp/elk
# Later
sudo docker container start elk

# Copy logstash config and results file to the container
sudo docker cp stats-csv.conf elk:/etc/logstash/conf.d/stats-csv.conf
sudo docker cp results.csv elk:/results.csv

# Login to the container
sudo docker exec -it elk /bin/bash

#------------------------
# On the container:

# Restart logstash to force it use new config to import tests stats
service logstash restart
