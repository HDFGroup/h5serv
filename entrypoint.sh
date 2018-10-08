#!/bin/bash
# entrypoint for Docker container
cd /usr/local/src/h5serv
python h5serv --datapath=/data --log_file=