#!/bin/bash

# we need to create the default hab user
sudo adduser --disabled-password --gecos "" hab
# assumes local package file
sudo tar zxvf *-table-setting*.tar.gz -C /
# run app in SQLite file mode
export DB_TYPE=sqlite_file
# install and run with the habitat supervisor
sudo /hab/bin/hab sup run &
sudo /hab/bin/hab svc load habskp/table-setting
