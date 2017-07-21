#!/bin/bash

CONTAINS=$(egrep -i "mongodb" /etc/hosts)

if [ -z "$CONTAINS" ]
then
  echo "127.0.0.1      mongodb" >> /etc/hosts
fi