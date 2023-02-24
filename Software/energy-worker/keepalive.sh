#!/bin/sh


file='/usr/src/app/exit'
while [ ! -f $file ]
do
   echo "To exit run: docker exed  <image> touch /usr/src/app/exit"
   sleep 2
done
rm /usr/src/app/exit