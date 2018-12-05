#!/bin/bash
set -e

COMMANDS="pserve document_publisher incomingmail_dispatcher deliberation_dispatcher outgoingmail_dispatcher outgoinggeneratedmail_dispatcher request_handler request_error"
CMD_BASE="/home/imio/imio.webservice.json/bin/"
CMD="$CMD_BASE/$1"

if [[ "$1" == "pserve"* ]]; then
  while ! nc -z postgres 5432;
  do
    echo "wait for postgres";
    sleep 1;
  done;
  echo "connected";
  exec $CMD "$2"
else
  while ! nc -z instance 6543;
  do
    echo "wait for pyramid";
    sleep 2;
  done;
  while ! nc -z rabbitmq 5672;
  do
    echo "wait for rabbitmq";
    sleep 2;
  done;
  echo "connected";
  exec $CMD "$2"
fi
