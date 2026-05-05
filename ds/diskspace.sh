#!/bin/bash

echo "The disk free space of the system is: "

sleep 1

df -h

echo "The list of blocked devices are:"

lsblk

sleep 1

echo "The top 10 directories space utilized are:"

du -sh /* 2>/dev/null | sort -hr | head -10

sleep 1

echo "The to 10 directories that are used by the var directory:"

if [ -d /var ]; then

	du -sh /var/* 2>/dev/null | sort -hr | head -10

else

	echo "var directories is not there"

fi

echo "Report Completed!"
