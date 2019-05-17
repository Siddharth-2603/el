#!/bin/bash

# make script executable
sudo chmod +x install-package.sh

# install required packages for Python 3
declare -a packages=("mysql-connector" "xlsxwriter" "tkcalendar" "babel")
for i in "${packages[@]}"
do
#	echo "$i"
	sudo pip3 install "$i"
done
