#!/bin/bash

#verification du service motion
service="motion"
if (( $(ps -ef | grep -v grep | grep $service | wc -l) > 0 ))
then
echo "$service is running!!!"
else
echo "$service is off, starting it ..." >> /home/pi/colibri/err.log
motion
fi

#execution de l'analyse d'image
python /home/pi/colibri/colibri.py >> /home/pi/colibri/err.log
